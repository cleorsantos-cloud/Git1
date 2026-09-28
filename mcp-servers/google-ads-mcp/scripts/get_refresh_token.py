#!/usr/bin/env python3
"""Gera o refresh token do OAuth para o google-ads-mcp.

Roda na SUA máquina, com navegador. Abre o consentimento do Google, você
entra com a conta que administra a MCC, e o refresh token sai no terminal.

Pré-requisitos:
  1. No Google Cloud Console, no mesmo projeto, habilite a Google Ads API.
  2. Crie uma credencial OAuth do tipo "App para computador" (Desktop app).
  3. pip install google-auth-oauthlib

Uso:
  python3 scripts/get_refresh_token.py --client-id XXX --client-secret YYY

  ou, se baixou o JSON da credencial:
  python3 scripts/get_refresh_token.py --client-secrets-file client_secret.json

O refresh token não expira enquanto não for revogado. Trate como senha:
guarde em variável de ambiente, nunca no repositório.
"""

import argparse
import json
import sys

SCOPES = ["https://www.googleapis.com/auth/adwords"]


def build_client_config(client_id: str, client_secret: str) -> dict:
    """Monta a configuração de cliente instalado, sem precisar do arquivo JSON."""
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gera o refresh token da Google Ads API."
    )
    parser.add_argument("--client-id", help="client ID do OAuth")
    parser.add_argument("--client-secret", help="client secret do OAuth")
    parser.add_argument(
        "--client-secrets-file",
        help="caminho do JSON baixado do Cloud Console (alternativa aos dois acima)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="porta do servidor local que recebe o retorno (padrão: 8080)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="não abre o navegador sozinho; imprime a URL para você colar",
    )
    args = parser.parse_args()

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print(
            "Falta a dependência. Rode antes:\n  pip install google-auth-oauthlib",
            file=sys.stderr,
        )
        return 1

    if args.client_secrets_file:
        flow = InstalledAppFlow.from_client_secrets_file(
            args.client_secrets_file, scopes=SCOPES
        )
    elif args.client_id and args.client_secret:
        flow = InstalledAppFlow.from_client_config(
            build_client_config(args.client_id, args.client_secret), scopes=SCOPES
        )
    else:
        parser.error(
            "informe --client-secrets-file, ou --client-id junto com --client-secret"
        )
        return 2

    print("Abrindo o consentimento do Google...")
    print("Entre com a conta que administra a MCC da agência.\n")

    credentials = flow.run_local_server(
        port=args.port,
        open_browser=not args.no_browser,
        access_type="offline",
        prompt="consent",
        authorization_prompt_message=(
            "Se o navegador não abrir sozinho, cole esta URL nele:\n{url}\n"
        ),
        success_message=(
            "Autorizado. Pode fechar esta aba e voltar para o terminal."
        ),
    )

    if not credentials.refresh_token:
        print(
            "\nO Google não devolveu refresh token. Isso acontece quando a conta "
            "já autorizou este cliente antes. Revogue o acesso em "
            "https://myaccount.google.com/permissions e rode de novo.",
            file=sys.stderr,
        )
        return 3

    print("\n" + "=" * 60)
    print("REFRESH TOKEN GERADO")
    print("=" * 60)
    print(f"\nGOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}\n")
    print("Exporte junto das outras variáveis e rode scripts/install.sh.")
    print("Não cole este valor em chat, ticket ou commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
