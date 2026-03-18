
import json
import imaplib
from pathlib import Path
from email import policy
from email.parser import BytesParser

from utils.assistants import get_last_uid
from utils.assistants import save_last_uid
from utils.assistants import sanitize_filename
from utils.assistants import extract_email_metadata


def lambda_handler(event=None, context=None) -> bool:
    try:
        IMAP_HOST = "imap.?????.com"
        IMAP_PORT = 993
        USERNAME = "contato@??????.br"
        PASSWORD = "???????"
        MAILBOX = "INBOX"

        BASE_DIR = Path("./tmp")
        EMAIL_DIR = BASE_DIR / "emails"
        UID_FILE = BASE_DIR / "last_uid.txt"

        EMAIL_DIR.mkdir(parents=True, exist_ok=True)
        BASE_DIR.mkdir(parents=True, exist_ok=True)

        last_uid = get_last_uid(UID_FILE)
        max_uid_processed = last_uid

        with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as mail:
            mail.login(USERNAME, PASSWORD)
            mail.select(MAILBOX)

            # Busca apenas UIDs maiores que o último processado
            status, data = mail.uid("search", None, f"UID {last_uid + 1}:*")

            if status != "OK":
                print("Erro na busca.")
                return False

            uid_list = data[0].split()

            for uid in uid_list:
                status, msg_data = mail.uid("fetch", uid, "(RFC822)")
                if status != "OK":
                    continue

                raw_email = msg_data[0][1]
                msg = BytesParser(policy=policy.default).parsebytes(raw_email)

                metadata = extract_email_metadata(msg)
                metadata["imap_uid"] = int(uid)

                subject_slug = sanitize_filename(metadata.get("subject"))

                file_name = f"{uid.decode()}-{subject_slug}.json"
                file_path = EMAIL_DIR / file_name

                with file_path.open("w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)

                print(f"Salvo: {file_path}")

                max_uid_processed = max(max_uid_processed, int(uid))

            mail.logout()

        if max_uid_processed > last_uid:
            save_last_uid(UID_FILE, max_uid_processed)

        print(
            {
                "statusCode": 200,
                "body": "Lambda Executada com Sucesso"
            }
        )
        return True
    except Exception as error:
        print(
            {
                "statusCode": 500,
                "body": f"Erro na Execução da Lambda: {error}"
            }
        )
        return False


if __name__ == "__main__":
    lambda_handler()
