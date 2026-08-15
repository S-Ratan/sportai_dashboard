from backend.app.db.supabase import supabase


def test_supabase_connection():
    try:
        result = (
            supabase
            .table("videos")
            .select("id, filename, status")
            .limit(5)
            .execute()
        )

        print("Supabase database connection successful")
        print("Videos:", result.data)

    except Exception as e:
        print("Supabase connection failed")
        print("Error:", e)


if __name__ == "__main__":
    test_supabase_connection()