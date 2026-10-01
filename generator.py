import os
import shutil
import zipfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from security_hardener import get_sso_environment, get_sso_provider_label

BASE_DIR = Path(__file__).parent

DB_IMAGES = {
    "postgresql": "postgres:16-alpine",
    "mysql": "mysql:8.0",
    "mariadb": "mariadb:11.2",
    "none": None,
}

DB_PORTS = {
    "postgresql": "5432",
    "mysql": "3306",
    "mariadb": "3306",
    "none": None,
}


def _env() -> Environment:
    loader = FileSystemLoader(str(BASE_DIR / "templates"))
    return Environment(
        loader=loader,
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _build_context(app_name, domain, port, db_type, enable_sso, sso_provider,
                   sso_client_id, sso_client_secret, sso_tenant_id, sso_domain,
                   framework, ai_result):
    app_name_safe = "".join(c for c in app_name if c.isalnum() or c in "-_").lower() or "app"
    context = {
        "app_name": app_name,
        "app_name_safe": app_name_safe,
        "domain": domain,
        "port": port,
        "db_type": db_type,
        "db_image": DB_IMAGES.get(db_type),
        "db_port": DB_PORTS.get(db_type),
        "enable_sso": enable_sso,
        "sso_provider": sso_provider,
        "sso_provider_label": get_sso_provider_label(sso_provider),
        "framework": framework,
        "ai_result": ai_result or {},
    }

    if enable_sso:
        context["sso_env"] = get_sso_environment(
            sso_provider, sso_client_id, sso_client_secret,
            sso_tenant_id, sso_domain, domain,
        )
    else:
        context["sso_env"] = {}

    return context


def generate_stack(app_name, domain, port, db_type, enable_sso, sso_provider,
                   sso_client_id, sso_client_secret, sso_tenant_id, sso_domain,
                   framework, source_dir, output_dir, ai_result=None):
    env = _env()
    context = _build_context(
        app_name, domain, port, db_type, enable_sso, sso_provider,
        sso_client_id, sso_client_secret, sso_tenant_id, sso_domain,
        framework, ai_result,
    )

    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    stack_dir = out / f"{context['app_name_safe']}-dockerstack"
    stack_dir.mkdir(exist_ok=True)
    apache_dir = stack_dir / "apache"
    apache_dir.mkdir(exist_ok=True)

    def render(name, target, **overrides):
        merged = dict(context)
        merged.update(overrides)
        content = env.get_template(name).render(**merged)
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    dockerfile_template = f"dockerfile/{framework}.j2"
    if not (BASE_DIR / "templates" / dockerfile_template).exists():
        dockerfile_template = "dockerfile/generic.j2"

    render(dockerfile_template, stack_dir / "Dockerfile", db_type=db_type)

    render("dockercompose.app.j2", stack_dir / "docker-compose.app.yaml",
           include_db=False, db_image=None, db_port=None)
    render("dockercompose.fulldb.j2", stack_dir / "docker-compose.fulldb.yaml",
           include_db=True)

    render("env.app.j2", stack_dir / ".env.example.app", include_db=False,
           db_image=None)
    render("env.fulldb.j2", stack_dir / ".env.example.fulldb", include_db=True)

    render("apache/app.conf.j2", apache_dir / "app.conf.template")
    render("apache/entrypoint.sh.j2", apache_dir / "entrypoint.sh")

    render("README.j2", stack_dir / "README.md")

    gitignore = stack_dir / ".gitignore"
    gitignore.write_text(
        ".env\n.env.*\n*.log\nnode_modules/\nvendor/\n__pycache__/\n", encoding="utf-8"
    )

    dockerignore = stack_dir / ".dockerignore"
    dockerignore.write_text(
        ".git\n.gitignore\n.dockerignore\n.env\n.env.*\n"
        "*.md\nnode_modules/\nvendor/\nstorage/logs/*\n"
        "storage/framework/cache/*\nstorage/framework/sessions/*\n"
        "storage/framework/views/*\ntests/\nphpunit.xml\n"
        "__pycache__/\n.docker/\n", encoding="utf-8"
    )

    if ai_result and "error" not in (ai_result or {}):
        render("aianalysis.j2", stack_dir / "aianalysis.md")

    return str(stack_dir)
