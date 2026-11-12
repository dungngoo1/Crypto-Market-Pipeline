import json
import os
from datetime import datetime, timezone
from pathlib import Path


import requests
from dotenv import load_dotenv

# Đường dẫn được tính từ vị trí file Python.
BASE_DIR = Path(__file__).resolve().parent


def main():
    # 1. Đọc cấu hình.
    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("MY_COINGECKO_API_KEY")

    if not api_key:
        print("Thiếu MY_COINGECKO_API_KEY trong file .env")
        return

    # 2. Gọi API để lấy danh sách category.
    url = "https://api.coingecko.com/api/v3/coins/categories/list"
    headers = {"x-cg-demo-api-key": api_key}

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )

        # Dừng nếu API trả lỗi HTTP, ví dụ 401 hoặc 429.
        response.raise_for_status()

        categories = response.json()

    except requests.RequestException as error:
        print(f"Gọi API thất bại: {error}")
        return

    except ValueError:
        print("API không trả về JSON hợp lệ.")
        return

    # 3. Kiểm tra sơ bộ cấu trúc response.
    if not isinstance(categories, list):
        print("Response không đúng cấu trúc mong đợi: cần một list.")
        return

    # 4. Lưu toàn bộ dữ liệu gốc trước khi chọn lọc.
    fetched_at = datetime.now(timezone.utc)
    timestamp = fetched_at.strftime("%Y%m%dT%H%M%S%fZ")

    output_dir = BASE_DIR / "data" / "raw" / "coingecko" / "categories"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"categories_{timestamp}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            categories,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Thời điểm lấy dữ liệu UTC: {fetched_at.isoformat()}")
    print(f"Số danh mục: {len(categories)}")
    print(f"Đã lưu: {output_path}")

    # 5. In các danh mục có tên liên quan để khảo sát.
    # Đây chỉ là tìm ứng viên, chưa phải quy tắc phân loại chính thức.
    keywords = (
        "artificial intelligence",
        "gaming",
        "gamefi",
        "decentralized finance",
        "defi",
        "real world",
        "rwa",
    )

    print("\nCác danh mục cần xem xét:")

    for category in categories:
        name = category.get("name") or ""
        category_id = category.get("category_id")

        if any(keyword in name.lower() for keyword in keywords):
            print(f"{category_id} | {name}")


if __name__ == "__main__":
    main()
