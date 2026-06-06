from app.app.db.supabase_client import get_supabase_admin, get_supabase_public


class AuthService:
    def __init__(self) -> None:
        self.public_client = get_supabase_public()
        self.admin_client = get_supabase_admin()

    def signup(self, email: str, password: str, metadata: dict) -> dict:
        response = self.public_client.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {"data": metadata},
            }
        )
        user = response.user
        session = response.session
        
        # If email confirmation is enabled, session will be None.
        # We should still allow the user to be created in the database.
        return {
            "user_id": user.id,
            "access_token": session.access_token if session else None,
            "refresh_token": session.refresh_token if session else None,
            "requires_confirmation": session is None
        }

    def login(self, email: str, password: str) -> dict:
        response = self.public_client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        if not response.user or not response.session:
            raise RuntimeError("Invalid credentials")

        return {
            "user_id": response.user.id,
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    def save_profile_and_preferences(self, user_id: str, payload: dict) -> None:
        try:
            self.admin_client.table("user_profiles").upsert(
                {
                    "user_id": user_id,
                    "full_name": payload["full_name"],
                    "learning_level": payload["learning_level"],
                    "preferred_explanation_style": payload["preferred_explanation_style"],
                    "preferred_learning_mode": payload["preferred_learning_mode"],
                    "subjects": payload["subjects"],
                }
            ).execute()

            self.admin_client.table("learning_preferences").insert(
                {
                    "user_id": user_id,
                    "explanation_style": payload["preferred_explanation_style"],
                    "learning_mode": payload["preferred_learning_mode"],
                    "subjects": payload["subjects"],
                    "learning_level": payload["learning_level"],
                    "is_active": True,
                }
            ).execute()
        except Exception as e:
            print(f"Error in save_profile_and_preferences: {str(e)}")
            # Even if DB profile fails, the auth user is created. 
            # We don't want to swallow the error but we need to know why.
            raise e
