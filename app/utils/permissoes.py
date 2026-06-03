from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


PERFIS_ADMINISTRATIVOS = ["coordenador", "secretaria", "bolsista"]


def perfil_required(*perfis_permitidos):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("usuarios.login"))

            if current_user.perfil not in perfis_permitidos:
                flash("Você não tem permissão para acessar esta página.", "danger")

                if current_user.perfil == "professor":
                    return redirect(url_for("frequencias.minhas_faltas"))

                return redirect(url_for("dashboard"))

            return func(*args, **kwargs)

        return wrapper

    return decorator


def administrativo_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("usuarios.login"))

        if current_user.perfil not in PERFIS_ADMINISTRATIVOS:
            flash("Você não tem permissão para acessar esta página.", "danger")

            if current_user.perfil == "professor":
                return redirect(url_for("frequencias.minhas_faltas"))

            return redirect(url_for("dashboard"))

        return func(*args, **kwargs)

    return wrapper