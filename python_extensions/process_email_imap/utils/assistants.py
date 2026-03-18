
import re
import base64
import unicodedata
from pathlib import Path
from typing import List, Dict
from email.header import decode_header


def get_last_uid(uid_file: Path) -> int:
    try:
        if uid_file.exists():
            return int(uid_file.read_text().strip())
        return 0
    except Exception as error:
        print(error)
        return 1


def save_last_uid(uid_file: Path, uid: int) -> bool:
    try:
        uid_file.write_text(str(uid))
        return True
    except Exception as error:
        print(error)
        return False


def _decode_mime_words(s) -> str:
    try:
        if not s:
            return ""
        decoded = decode_header(s)
        return "".join(
            str(t[0], t[1] or "utf-8") if isinstance(t[0], bytes) else t[0]
            for t in decoded
        )
    except Exception as error:
        print(error)
        return ""


def sanitize_filename(text) -> str:
    try:
        text = _decode_mime_words(text)
        text = (
            unicodedata
            .normalize("NFKD", text)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        text = re.sub(r"[^\w\s-]", "", text).strip().lower()
        text = re.sub(r"[-\s]+", "-", text)
        return text[:120] if text else "sem-assunto"
    except Exception as error:
        print(error)
        return "sem-assunto"


def extract_email_metadata(msg) -> List[Dict]:
    metadata = {}

    for k, v in msg.items():
        metadata[k.lower()] = _decode_mime_words(v)

    metadata["subject"] = _decode_mime_words(msg.get("Subject"))
    metadata["from"] = _decode_mime_words(msg.get("From"))
    metadata["to"] = _decode_mime_words(msg.get("To"))
    metadata["cc"] = _decode_mime_words(msg.get("Cc"))
    metadata["bcc"] = _decode_mime_words(msg.get("Bcc"))
    metadata["date"] = _decode_mime_words(msg.get("Date"))
    metadata["message_id"] = _decode_mime_words(msg.get("Message-ID"))

    metadata["body"] = {"text": None, "html": None}
    metadata["attachments"] = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" in content_disposition:
                file_name = part.get_filename()
                if file_name:
                    file_name = _decode_mime_words(file_name)
                    file_content = part.get_payload(decode=True)
                    metadata["attachments"].append({
                        "content_type": content_type,
                        "file_name": file_name,
                        "file_content_base64": (
                            base64.b64encode(file_content).decode()
                        )
                    })

            elif (
                content_type == "text/plain"
                and metadata["body"]["text"] is None
            ):
                payload = part.get_payload(decode=True)
                if payload:
                    metadata["body"]["text"] = payload.decode(errors="ignore")

            elif (
                content_type == "text/html"
                and metadata["body"]["html"] is None
            ):
                payload = part.get_payload(decode=True)
                if payload:
                    metadata["body"]["html"] = payload.decode(errors="ignore")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            metadata["body"]["text"] = payload.decode(errors="ignore")

    return metadata
