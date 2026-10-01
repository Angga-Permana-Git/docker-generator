SSO_PROVIDERS = {
    "keycloak": {
        "label": "Keycloak",
        "env": {
            "SSO_PROVIDER": "keycloak",
            "KEYCLOAK_URL": "https://keycloak.example.com",
            "KEYCLOAK_REALM": "your-realm",
            "SSO_CLIENT_ID": "{sso_client_id}",
            "SSO_CLIENT_SECRET": "{sso_client_secret}",
            "SSO_ISSUER_URL": "https://keycloak.example.com/realms/your-realm",
            "SSO_AUTHORIZATION_URL": "https://keycloak.example.com/realms/your-realm/protocol/openid-connect/auth",
            "SSO_TOKEN_URL": "https://keycloak.example.com/realms/your-realm/protocol/openid-connect/token",
            "SSO_USERINFO_URL": "https://keycloak.example.com/realms/your-realm/protocol/openid-connect/userinfo",
            "SSO_REDIRECT_URI": "https://{domain}/callback",
        },
    },
    "auth0": {
        "label": "Auth0",
        "env": {
            "SSO_PROVIDER": "auth0",
            "AUTH0_DOMAIN": "your-tenant.auth0.com",
            "SSO_CLIENT_ID": "{sso_client_id}",
            "SSO_CLIENT_SECRET": "{sso_client_secret}",
            "SSO_ISSUER_URL": "https://your-tenant.auth0.com/",
            "SSO_AUTHORIZATION_URL": "https://your-tenant.auth0.com/authorize",
            "SSO_TOKEN_URL": "https://your-tenant.auth0.com/oauth/token",
            "SSO_USERINFO_URL": "https://your-tenant.auth0.com/userinfo",
            "SSO_REDIRECT_URI": "https://{domain}/callback",
        },
    },
    "azuread": {
        "label": "Azure AD",
        "env": {
            "SSO_PROVIDER": "azuread",
            "AZURE_TENANT_ID": "{sso_tenant_id}",
            "SSO_CLIENT_ID": "{sso_client_id}",
            "SSO_CLIENT_SECRET": "{sso_client_secret}",
            "SSO_ISSUER_URL": "https://login.microsoftonline.com/{sso_tenant_id}/v2.0",
            "SSO_AUTHORIZATION_URL": "https://login.microsoftonline.com/{sso_tenant_id}/oauth2/v2.0/authorize",
            "SSO_TOKEN_URL": "https://login.microsoftonline.com/{sso_tenant_id}/oauth2/v2.0/token",
            "SSO_REDIRECT_URI": "https://{domain}/callback",
        },
    },
    "generic": {
        "label": "Generic OIDC",
        "env": {
            "SSO_PROVIDER": "generic",
            "OIDC_DOMAIN": "{sso_domain}",
            "SSO_CLIENT_ID": "{sso_client_id}",
            "SSO_CLIENT_SECRET": "{sso_client_secret}",
            "SSO_ISSUER_URL": "https://{sso_domain}/.well-known/openid-configuration",
            "SSO_AUTHORIZATION_URL": "https://{sso_domain}/authorize",
            "SSO_TOKEN_URL": "https://{sso_domain}/token",
            "SSO_USERINFO_URL": "https://{sso_domain}/userinfo",
            "SSO_REDIRECT_URI": "https://{domain}/callback",
        },
    },
    "genericpmk": {
        "label": "Generic OIDC (Custom)",
        "env": {
            "SSO_PROVIDER": "genericpmk",
            "SSO_URL": "https://{sso_domain}",
            "SSO_LOGIN_URL": "/login?requestId=",
            "SSO_ORIGIN": "https://{sso_domain}",
            "SSO_CLIENT_KEY": "{sso_client_id}",
            "SSO_CLIENT_SECRET": "{sso_client_secret}",
            "SSO_TLS_VERIFY": "false",
            "SSO_REDIRECT_URI": "https://{domain}/callback",
            "SERVER_HOST": "{domain}",
            "COOKIE_DOMAIN": ".{domain}",
        },
    },
}


def get_sso_environment(provider: str, sso_client_id: str, sso_client_secret: str,
                        sso_tenant_id: str, sso_domain: str, app_domain: str) -> dict:
    provider = provider.lower()
    spec = SSO_PROVIDERS.get(provider, SSO_PROVIDERS["generic"])
    env = {}
    for key, value in spec["env"].items():
        value = value.replace("{sso_client_id}", sso_client_id or "change-me")
        value = value.replace("{sso_client_secret}", sso_client_secret or "change-me")
        value = value.replace("{sso_tenant_id}", sso_tenant_id or "change-me")
        value = value.replace("{sso_domain}", sso_domain or "sso.example.com")
        value = value.replace("{domain}", app_domain)
        env[key] = value
    return env


def get_sso_provider_label(provider: str) -> str:
    return SSO_PROVIDERS.get(provider.lower(), SSO_PROVIDERS["generic"])["label"]
