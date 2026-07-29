import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import os
import sys
import time
import random
import queue
from io import BytesIO

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# 确保能找到核心模块（兼容PyInstaller打包后的路径）
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
import 秀人网提取 as xr


class XiuRenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("秀人网 · 图片提取工具")
        self.root.geometry("1050x720")
        self.root.minsize(900, 600)

        # 状态变量
        self.current_works = []
        self.current_info = None
        self.current_img_data = None
        self.preview_thumbnails = []
        self.download_dir = xr.SAVE_DIR
        self.download_delay = tk.DoubleVar(value=1.0)  # 下载间隔（秒）
        self.dl_queue = queue.Queue()  # 下载线程→主线程的通信队列
        self._start_dl_poller()

        self.setup_ui()
        self.init_session()

    def setup_ui(self):
        # ===== 顶部标题栏 =====
        title_frame = ttk.Frame(self.root, padding=(10, 8))
        title_frame.pack(fill=tk.X)

        ttk.Label(title_frame, text="秀人网 · 图片提取工具",
                  font=("Microsoft YaHei UI", 16, "bold")).pack(side=tk.LEFT)

        ttk.Button(title_frame, text="设置下载目录",
                   command=self.set_download_dir).pack(side=tk.RIGHT)

        # ===== 搜索栏 =====
        search_frame = ttk.Frame(self.root, padding=(10, 0, 10, 5))
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="关键词:").pack(side=tk.LEFT)
        self.keyword_entry = ttk.Entry(search_frame, width=25)
        self.keyword_entry.pack(side=tk.LEFT, padx=4)
        self.keyword_entry.bind("<Return>", lambda e: self.search())
        ttk.Button(search_frame, text="搜索", command=self.search).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="浏览最新", command=self.browse).pack(side=tk.LEFT, padx=2)

        ttk.Separator(search_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=12, fill=tk.Y)

        ttk.Label(search_frame, text="work_id:").pack(side=tk.LEFT)
        self.wid_entry = ttk.Entry(search_frame, width=10)
        self.wid_entry.pack(side=tk.LEFT, padx=4)
        self.wid_entry.bind("<Return>", lambda e: self.view_by_wid())
        ttk.Button(search_frame, text="查看", command=self.view_by_wid).pack(side=tk.LEFT, padx=2)

        # 下载速度控制
        ttk.Separator(search_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Label(search_frame, text="速度:").pack(side=tk.LEFT)
        speed_combo = ttk.Combobox(search_frame, textvariable=self.download_delay,
                                   values=[0.3, 0.5, 1.0, 2.0, 3.0],
                                   width=4, state="readonly")
        speed_combo.pack(side=tk.LEFT, padx=2)
        ttk.Label(search_frame, text="秒间隔").pack(side=tk.LEFT)

        # ===== 主区域 =====
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=2, uniform="group")
        main_frame.columnconfigure(1, weight=3, uniform="group")
        main_frame.rowconfigure(0, weight=1)

        # ---- 左：作品列表 ----
        list_frame = ttk.LabelFrame(main_frame, text="作品列表", padding=5)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.work_listbox = tk.Listbox(list_frame, font=("Microsoft YaHei UI", 10),
                                       selectmode=tk.SINGLE, relief=tk.FLAT, bd=1)
        self.work_listbox.pack(fill=tk.BOTH, expand=True)
        self.work_listbox.bind("<<ListboxSelect>>", self.on_work_select)

        # ---- 右：作品详情 ----
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        detail_frame = ttk.LabelFrame(right_frame, text="作品详情", padding=5)
        detail_frame.grid(row=0, column=0, sticky="nsew")
        detail_frame.rowconfigure(0, weight=1)
        detail_frame.columnconfigure(0, weight=1)

        self.detail_text = tk.Text(detail_frame, font=("Microsoft YaHei UI", 10),
                                   wrap=tk.WORD, state=tk.DISABLED, relief=tk.FLAT, bd=1)
        self.detail_text.pack(fill=tk.BOTH, expand=True)

        # ---- 预览缩略图区域 ----
        preview_frame = ttk.LabelFrame(right_frame, text="预览缩略图", padding=5)
        preview_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        self.preview_canvas = tk.Canvas(preview_frame, height=130, highlightthickness=0)
        self.preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL,
                                             command=self.preview_canvas.xview)
        self.preview_canvas.configure(xscrollcommand=self.preview_scroll.set)

        self.preview_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.preview_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.preview_inner = ttk.Frame(self.preview_canvas)
        self.preview_canvas.create_window((0, 0), window=self.preview_inner, anchor="nw")

        self.preview_inner.bind("<Configure>",
                                lambda e: self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all")))

        # ---- 下载进度面板（默认隐藏） ----
        self.dl_progress_frame = ttk.LabelFrame(right_frame, text="下载进度", padding=8)
        self.dl_progress_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        self.dl_progress_frame.grid_remove()  # 初始隐藏

        self.dl_file_var = tk.StringVar(value="")
        ttk.Label(self.dl_progress_frame, textvariable=self.dl_file_var,
                  font=("Consolas", 10)).pack(anchor=tk.W, fill=tk.X)

        self.dl_progress_bar = ttk.Progressbar(self.dl_progress_frame, mode='determinate')
        self.dl_progress_bar.pack(fill=tk.X, pady=4)

        self.dl_status_var = tk.StringVar(value="")
        ttk.Label(self.dl_progress_frame, textvariable=self.dl_status_var,
                  font=("Microsoft YaHei UI", 9)).pack(anchor=tk.W)

        # ---- 操作按钮 ----
        btn_frame = ttk.Frame(right_frame)
        btn_frame.grid(row=3, column=0, sticky="ew", pady=(8, 0))

        ttk.Button(btn_frame, text="打开预览图", command=self.open_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="查看全部图片", command=self.view_images).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="下载全部图片", command=self.download_all).pack(side=tk.LEFT, padx=2)

        # ===== 底部状态栏 =====
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="正在连接...")
        ttk.Label(status_frame, textvariable=self.status_var, padding=(8, 3)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.dl_info_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.dl_info_var, padding=(8, 3),
                  font=("Consolas", 9)).pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(status_frame, mode='determinate', length=200)
        self.progress.pack(side=tk.RIGHT, padx=8, pady=3)

    # ==================== 核心功能 ====================

    def init_session(self):
        def task():
            ok = xr.init_session()
            self.root.after(0, lambda: self.status_var.set(
                "连接成功 - 就绪" if ok else "连接失败，请检查网络"))
        threading.Thread(target=task, daemon=True).start()

    def set_download_dir(self):
        d = filedialog.askdirectory(title="选择下载目录", initialdir=self.download_dir)
        if d:
            self.download_dir = d
            xr.SAVE_DIR = d
            self.status_var.set(f"下载目录已设置为: {d}")

    def search(self):
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            return
        self.set_status(f'正在搜索 "{keyword}"...')
        self.start_progress(mode='indeterminate')
        threading.Thread(target=self._search_task, args=(keyword,), daemon=True).start()

    def _search_task(self, keyword):
        works = xr.search_works(keyword)
        self.root.after(0, self._display_works, works)

    def browse(self):
        self.set_status("正在获取最新作品...")
        self.start_progress(mode='indeterminate')
        threading.Thread(target=self._browse_task, daemon=True).start()

    def _browse_task(self):
        works = xr.list_recent_works(3)
        self.root.after(0, self._display_works, works)

    def _display_works(self, works):
        self.stop_progress()
        self.work_listbox.delete(0, tk.END)
        self.current_works = works
        if not works:
            self.set_status("未找到作品")
            return
        for i, w in enumerate(works, 1):
            self.work_listbox.insert(tk.END, f"  [{i}] {w['title']}")
        self.set_status(f"找到 {len(works)} 个作品  |  下载至: {self.download_dir}")

    def view_by_wid(self):
        wid = self.wid_entry.get().strip()
        if not wid or not wid.isdigit():
            messagebox.showwarning("提示", "请输入有效的 work_id 数字")
            return
        self.set_status(f"正在查询 work_id={wid}...")
        self.start_progress(mode='indeterminate')
        threading.Thread(target=self._view_by_wid_task, args=(int(wid),), daemon=True).start()

    def _view_by_wid_task(self, wid):
        data = xr.fetch_images(wid)
        self.root.after(0, self._on_wid_result, wid, data)

    def _on_wid_result(self, wid, data):
        self.stop_progress()
        if not data or not data.get("ok"):
            self.set_status(f"work_id={wid} 无效")
            messagebox.showerror("错误", f"work_id={wid} 无效，API返回: {data}")
            return
        # 构造一个伪 info
        info = {
            "work_id": wid,
            "title": f"作品 #{wid}",
            "description": "",
            "total": data.get("total", 0),
            "preview_urls": [],
        }
        self.current_info = info
        self.current_img_data = data
        self.show_detail(info)
        self.show_images_in_detail(data)
        self.set_status(f"work_id={wid} 有效，共 {info['total']} 张图片")

    # ==================== 作品选择 ====================

    def on_work_select(self, event):
        sel = self.work_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self.current_works):
            return
        w = self.current_works[idx]
        self.set_status(f"获取详情: {w['title'][:40]}...")
        self.start_progress(mode='indeterminate')
        threading.Thread(target=self._load_detail_task, args=(w['url'],), daemon=True).start()

    def _load_detail_task(self, url):
        info = xr.get_work_info(url)
        if info and info.get("work_id"):
            data = xr.fetch_images(info["work_id"])
        else:
            data = None
        self.root.after(0, self._display_detail, info, data)

    def _display_detail(self, info, data):
        self.stop_progress()
        if not info:
            self.set_status("获取详情失败")
            return
        self.current_info = info
        self.current_img_data = data
        self.show_detail(info)
        self.show_images_in_detail(data)
        self.set_status(f"详情: {info['title'][:50]}...  |  下载至: {self.download_dir}")

    # ==================== 显示详情 ====================

    def show_detail(self, info):
        self.detail_text.configure(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, f"标题: {info['title']}\n\n")
        self.detail_text.insert(tk.END, f"work_id: {info['work_id']}\n")
        self.detail_text.insert(tk.END, f"图片总数: {info['total']} 张\n\n")
        if info.get("description"):
            self.detail_text.insert(tk.END, f"描述: {info['description']}\n")
        self.detail_text.configure(state=tk.DISABLED)

    def show_images_in_detail(self, data):
        """在预览区显示可点击的预览按钮"""
        for w in self.preview_inner.winfo_children():
            w.destroy()
        self.preview_thumbnails = []

        if not data:
            ttk.Label(self.preview_inner, text="暂无图片数据").pack(side=tk.LEFT, padx=10)
            return

        items = data.get("items", [])
        if not items:
            ttk.Label(self.preview_inner, text="暂无预览图").pack(side=tk.LEFT, padx=10)
            return

        for idx, url in enumerate(items[:8], 1):
            frame = ttk.Frame(self.preview_inner)
            frame.pack(side=tk.LEFT, padx=3)

            # 用按钮显示预览，点击在浏览器打开
            fname = url.split("/")[-1]
            btn = ttk.Button(frame, text=f"[{idx}]\n{fname[:12]}",
                             width=12,
                             command=lambda u=url: webbrowser.open(u))
            btn.pack()
            # 下载按钮
            dl_btn = ttk.Button(frame, text="下载",
                                command=lambda u=url, n=fname: self._dl_single(u, n))
            dl_btn.pack(pady=(2, 0))

    def _dl_single(self, url, fname):
        """下载单张预览图到桌面"""
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        save_path = os.path.join(desktop, fname)
        threading.Thread(target=self._dl_single_task, args=(url, save_path), daemon=True).start()

    def _dl_single_task(self, url, save_path):
        ok = xr.download_image(url, save_path)
        self.root.after(0, lambda: self.set_status(
            f"下载完成: {os.path.basename(save_path)}" if ok else "下载失败"))

    # ==================== 操作按钮 ====================

    def open_preview(self):
        if not self.current_info:
            messagebox.showwarning("提示", "请先选择一个作品")
            return
        urls = self.current_info.get("preview_urls", [])
        if not urls and self.current_img_data:
            urls = self.current_img_data.get("items", [])[:1]
        if urls:
            webbrowser.open(urls[0])
            preview_count = len(self.current_info.get("preview_urls", []))
            total = self.current_info.get("total", 0)
            self.set_status(f"已打开第1张预览 (共{preview_count}张预览 / {total}张全图)")

    def view_images(self):
        if not self.current_info:
            messagebox.showwarning("提示", "请先选择一个作品")
            return
        ImageWindow(self.root, self.current_info, self.current_img_data)

    def download_all(self):
        if not self.current_info:
            messagebox.showwarning("提示", "请先选择一个作品")
            return
        threading.Thread(target=self._download_task, daemon=True).start()

    def _start_dl_poller(self):
        """定期从队列读取下载进度并更新UI"""
        try:
            while True:
                msg = self.dl_queue.get_nowait()
                typ = msg.get("type")
                if typ == "progress":
                    i, total, fname, pct, status = msg["i"], msg["total"], msg["fname"], msg["pct"], msg["status"]
                    # 显示进度面板
                    if not self.dl_progress_frame.winfo_ismapped():
                        self.dl_progress_frame.grid()
                    self.dl_file_var.set(f"[{i}/{total}] {fname}")
                    self.dl_progress_bar.configure(value=pct or 0)
                    self.dl_status_var.set(status)
                    self.set_status(status)
                elif typ == "done":
                    self.dl_progress_bar.stop()
                    self.dl_progress_frame.grid_remove()
                    total, success, save_dir = msg["total"], msg["success"], msg["save_dir"]
                    self.set_status(f"下载完成: {success}/{total} 张 -> {save_dir}")
                    messagebox.showinfo("下载完成", f"成功下载 {success}/{total} 张\n保存至: {save_dir}")
                elif typ == "error":
                    self.dl_progress_bar.stop()
                    self.dl_progress_frame.grid_remove()
                    self.set_status(msg.get("text", "下载失败"))
        except queue.Empty:
            pass
        self.root.after(200, self._start_dl_poller)

    def _download_task(self):
        info = self.current_info
        folder = xr.safe_filename(info["title"])
        save_dir = os.path.join(xr.SAVE_DIR, folder)

        self.dl_queue.put({"type": "progress", "i": 0, "total": 0, "fname": "正在收集图片URL...",
                           "pct": 0, "status": "正在收集全部图片URL..."})
        self.root.after(0, lambda: self.dl_progress_bar.configure(mode='indeterminate'))
        self.root.after(0, lambda: self.dl_progress_bar.start(10))

        all_urls = xr.collect_all_images(info["work_id"])
        if not all_urls:
            self.dl_queue.put({"type": "error", "text": "收集图片失败"})
            self.root.after(0, self.stop_progress)
            return

        total = len(all_urls)
        os.makedirs(save_dir, exist_ok=True)
        success = 0

        for i, url in enumerate(all_urls, 1):
            ext = os.path.splitext(url.split("/")[-1])[1] or ".jpg"
            fname = f"{folder}_{i:03d}{ext}"
            save_path = os.path.join(save_dir, fname)
            pct = i / total * 100

            # 通过队列发送进度更新，主线程 poller 会处理
            self.dl_queue.put({
                "type": "progress",
                "i": i, "total": total, "fname": fname,
                "pct": pct, "status": f"下载中 ({i}/{total})"
            })

            ok = xr.download_image(url, save_path)
            if ok:
                success += 1
                self.dl_queue.put({
                    "type": "progress",
                    "i": i, "total": total, "fname": fname + " OK",
                    "pct": pct, "status": f"已下载 {i}/{total}"
                })
            else:
                self.dl_queue.put({
                    "type": "progress",
                    "i": i, "total": total, "fname": fname + " 失败",
                    "pct": pct, "status": f"下载失败 {i}/{total}"
                })

            if i < total:
                delay = self.download_delay.get()
                time.sleep(random.uniform(delay * 0.7, delay * 1.3))

        self.dl_queue.put({
            "type": "done",
            "total": total, "success": success, "save_dir": save_dir
        })

    # ==================== 工具方法 ====================

    def set_status(self, msg):
        self.status_var.set(msg)

    def start_progress(self, mode='indeterminate'):
        self.progress.configure(mode=mode)
        if mode == 'indeterminate':
            self.progress.start(10)
        else:
            self.progress.configure(value=0)

    def stop_progress(self):
        self.progress.stop()
        self.progress.configure(value=0, mode='determinate')


# ==================== 图片列表窗口 ====================

class ImageWindow:
    def __init__(self, parent, info, img_data):
        self.parent = parent
        self.info = info
        self.current_img_data = img_data
        self.work_id = info["work_id"]
        self.title = info["title"]
        self.total = info.get("total", 0)

        self.win = tk.Toplevel(parent)
        self.win.title(f"图片列表 - {self.title[:30]}")
        self.win.geometry("700x500")
        self.win.transient(parent)

        self.setup_ui()
        self.display_page(1, img_data)

    def setup_ui(self):
        # 顶部信息
        top = ttk.Frame(self.win, padding=8)
        top.pack(fill=tk.X)

        self.info_label = ttk.Label(top, text="", font=("Microsoft YaHei UI", 10))
        self.info_label.pack(side=tk.LEFT)

        # 图片列表
        list_frame = ttk.Frame(self.win, padding=8)
        list_frame.pack(fill=tk.BOTH, expand=True)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        text_frame = ttk.Frame(list_frame)
        text_frame.grid(row=0, column=0, sticky="nsew")

        self.text_area = tk.Text(text_frame, font=("Consolas", 10), wrap=tk.NONE,
                                 state=tk.DISABLED)
        vbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        hbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text_area.xview)
        self.text_area.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 底部按钮
        btn_frame = ttk.Frame(self.win, padding=8)
        btn_frame.pack(fill=tk.X)

        self.page_var = tk.StringVar(value="")
        ttk.Label(btn_frame, textvariable=self.page_var).pack(side=tk.LEFT)

        ttk.Button(btn_frame, text="上一页", command=self.prev_page).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="下一页", command=self.next_page).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="打开浏览器查看", command=self.open_in_browser).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="关闭", command=self.win.destroy).pack(side=tk.RIGHT, padx=4)

    def make_urls_clickable(self):
        """给文本中的URL加tag，点击可打开"""
        self.text_area.tag_configure("url", foreground="#0066cc", underline=True)
        self.text_area.tag_bind("url", "<Button-1>", self._on_url_click)
        self.text_area.tag_bind("url", "<Enter>", lambda e: self.text_area.configure(cursor="hand2"))
        self.text_area.tag_bind("url", "<Leave>", lambda e: self.text_area.configure(cursor=""))

    def _on_url_click(self, event):
        """点击URL时在浏览器打开"""
        index = self.text_area.index(f"@{event.x},{event.y}")
        tags = self.text_area.tag_names(index)
        if "url" in tags:
            # 获取这个tag范围内的文本
            start = self.text_area.index(f"{index} linestart")
            end = self.text_area.index(f"{index} lineend")
            line = self.text_area.get(start, end).strip()
            # 提取URL（去掉前面的 [N] 编号）
            import re as _re
            m = _re.search(r'https?://\S+', line)
            if m:
                webbrowser.open(m.group())

    def display_page(self, page, data):
        self.current_page = page
        self.current_img_data = data
        if not data:
            return

        items = data.get("items", [])
        has_more = data.get("has_more", False)
        per_page = data.get("per_page", 12)
        total = data.get("total", self.total)

        self.text_area.configure(state=tk.NORMAL, cursor="")
        self.text_area.delete(1.0, tk.END)
        self.make_urls_clickable()
        self.text_area.insert(tk.END, f"共 {total} 张图片  |  第 {page} 页  |  点击链接打开\n")
        self.text_area.insert(tk.END, "=" * 60 + "\n\n")
        for i, url in enumerate(items, 1):
            idx = (page - 1) * per_page + i
            self.text_area.insert(tk.END, f"  [{idx}] ")
            tag_name = f"url_{idx}"
            self.text_area.tag_configure(tag_name, foreground="#0066cc", underline=True)
            self.text_area.insert(tk.END, url, tag_name)
            self.text_area.insert(tk.END, "\n\n")
            # 绑定点击
            self.text_area.tag_bind(tag_name, "<Button-1>",
                                    lambda e, u=url: webbrowser.open(u))
            self.text_area.tag_bind(tag_name, "<Enter>",
                                    lambda e: self.text_area.configure(cursor="hand2"))
            self.text_area.tag_bind(tag_name, "<Leave>",
                                    lambda e: self.text_area.configure(cursor=""))
        self.text_area.configure(state=tk.DISABLED)

        self.page_var.set(f"第 {page} 页  |  显示 {len(items)} 张")
        self.has_more = has_more
        self.next_token = data.get("next_token")

    def next_page(self):
        if not self.has_more or not self.next_token:
            messagebox.showinfo("提示", "已到最后一页")
            return
        threading.Thread(target=self._load_page, daemon=True).start()

    def prev_page(self):
        if self.current_page <= 1:
            messagebox.showinfo("提示", "已是第一页")
            return
        # 往前翻需要重新获取，直接调API
        threading.Thread(target=self._load_prev_page, daemon=True).start()

    def _load_page(self):
        params_img = {
            "work_id": self.work_id,
            "page": self.current_page + 1,
            "per_page": 12,
            "token": self.next_token,
        }
        resp = xr.session.get(xr.api_url, params=params_img,
                              headers=xr.headers, timeout=15)
        data = resp.json()
        if data and data.get("ok"):
            self.parent.after(0, lambda: self.display_page(self.current_page + 1, data))

    def _load_prev_page(self):
        data = xr.fetch_images(self.work_id, page=self.current_page - 1)
        if data and data.get("ok"):
            self.parent.after(0, lambda: self.display_page(self.current_page - 1, data))

    def open_in_browser(self):
        if not self.current_img_data:
            return
        items = self.current_img_data.get("items", [])
        if items:
            webbrowser.open(items[0])
            self.parent.set_status(f"已打开第{self.current_page}页第1张图片")


# ==================== 入口 ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = XiuRenApp(root)
    root.mainloop()
