import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from email.utils import formatdate, make_msgid, formataddr
from pathlib import Path
from typing import Any


class SmtpError(Exception):
    pass


class Attachment:
    def __init__(self, path: str, filename: str | None = None, cid: str | None = None) -> None:
        self.path = Path(path)
        self.filename = filename or self.path.name
        self.cid = cid
        self.inline = cid is not None

    def read(self) -> bytes:
        return self.path.read_bytes()

    def mime_type(self) -> tuple[str, str]:
        mime, _ = mimetypes.guess_type(str(self.path))
        if mime:
            main, sub = mime.split("/", 1)
            return main, sub
        return "application", "octet-stream"


class EmailMessage:
    def __init__(self) -> None:
        self._from: str = ""
        self._to: list[str] = []
        self._cc: list[str] = []
        self._bcc: list[str] = []
        self._reply_to: str = ""
        self._subject: str = ""
        self._text: str = ""
        self._html: str = ""
        self._attachments: list[Attachment] = []
        self._headers: dict[str, str] = {}

    def from_addr(self, address: str, name: str = "") -> "EmailMessage":
        self._from = formataddr((name, address)) if name else address
        return self

    def to(self, *addresses: str) -> "EmailMessage":
        self._to.extend(addresses)
        return self

    def cc(self, *addresses: str) -> "EmailMessage":
        self._cc.extend(addresses)
        return self

    def bcc(self, *addresses: str) -> "EmailMessage":
        self._bcc.extend(addresses)
        return self

    def reply_to(self, address: str) -> "EmailMessage":
        self._reply_to = address
        return self

    def subject(self, text: str) -> "EmailMessage":
        self._subject = text
        return self

    def text(self, body: str) -> "EmailMessage":
        self._text = body
        return self

    def html(self, body: str) -> "EmailMessage":
        self._html = body
        return self

    def attach(self, path: str, filename: str | None = None) -> "EmailMessage":
        self._attachments.append(Attachment(path, filename))
        return self

    def embed(self, path: str, cid: str) -> "EmailMessage":
        self._attachments.append(Attachment(path, cid=cid))
        return self

    def header(self, key: str, value: str) -> "EmailMessage":
        self._headers[key] = value
        return self

    def build(self) -> MIMEMultipart | MIMEText:
        has_attach = any(not a.inline for a in self._attachments)
        has_inline = any(a.inline for a in self._attachments)
        has_html = bool(self._html)
        has_text = bool(self._text)

        # Build body (innermost content)
        if has_text and has_html:
            if has_inline:
                related = MIMEMultipart("related")
                related.attach(MIMEText(self._html, "html", "utf-8"))
                for a in self._attachments:
                    if a.inline:
                        img = MIMEImage(a.read())
                        img.add_header("Content-ID", f"<{a.cid}>")
                        img.add_header("Content-Disposition", "inline", filename=a.filename)
                        related.attach(img)
                body: Any = MIMEMultipart("alternative")
                body.attach(MIMEText(self._text, "plain", "utf-8"))
                body.attach(related)
            else:
                body = MIMEMultipart("alternative")
                body.attach(MIMEText(self._text, "plain", "utf-8"))
                body.attach(MIMEText(self._html, "html", "utf-8"))
        elif has_html:
            if has_inline:
                body = MIMEMultipart("related")
                body.attach(MIMEText(self._html, "html", "utf-8"))
                for a in self._attachments:
                    if a.inline:
                        img = MIMEImage(a.read())
                        img.add_header("Content-ID", f"<{a.cid}>")
                        img.add_header("Content-Disposition", "inline", filename=a.filename)
                        body.attach(img)
            else:
                body = MIMEText(self._html, "html", "utf-8")
        elif has_text:
            body = MIMEText(self._text, "plain", "utf-8")
        else:
            body = MIMEText("", "plain", "utf-8")

        # Wrap in mixed container if there are file attachments
        if has_attach:
            root: Any = MIMEMultipart("mixed")
            root.attach(body)
            for a in self._attachments:
                if a.inline:
                    continue
                main_type, sub_type = a.mime_type()
                if main_type == "text":
                    part: Any = MIMEText(a.read().decode("utf-8", errors="replace"), sub_type)
                elif main_type == "image":
                    part = MIMEImage(a.read(), _subtype=sub_type)
                else:
                    part = MIMEBase(main_type, sub_type)
                    part.set_payload(a.read())
                    encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment", filename=a.filename)
                root.attach(part)
        else:
            root = body

        # Set envelope headers on the outermost object
        root["From"] = self._from
        root["To"] = ", ".join(self._to)
        if self._cc:
            root["Cc"] = ", ".join(self._cc)
        if self._reply_to:
            root["Reply-To"] = self._reply_to
        root["Subject"] = self._subject
        root["Date"] = formatdate(localtime=True)
        root["Message-ID"] = make_msgid()
        for k, v in self._headers.items():
            root[k] = v

        return root

    def all_recipients(self) -> list[str]:
        return self._to + self._cc + self._bcc


class SmtpClient:
    def __init__(
        self,
        host: str,
        port: int = 587,
        *,
        username: str = "",
        password: str = "",
        use_tls: bool = True,
        use_ssl: bool = False,
        timeout: float = 10.0,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.timeout = timeout
        self._conn: smtplib.SMTP | smtplib.SMTP_SSL | None = None

    def connect(self) -> "SmtpClient":
        try:
            if self.use_ssl:
                self._conn = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                self._conn = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                if self.use_tls:
                    self._conn.starttls()
            if self.username:
                self._conn.login(self.username, self.password)
        except smtplib.SMTPException as e:
            raise SmtpError(str(e)) from e
        return self

    def disconnect(self) -> None:
        if self._conn:
            try:
                self._conn.quit()
            except Exception:
                pass
            self._conn = None

    def __enter__(self) -> "SmtpClient":
        return self.connect()

    def __exit__(self, *_) -> None:
        self.disconnect()

    def send(self, message: EmailMessage) -> None:
        if self._conn is None:
            raise SmtpError("Not connected. Call connect() first.")
        try:
            mime = message.build()
            self._conn.sendmail(
                message._from,
                message.all_recipients(),
                mime.as_string(),
            )
        except smtplib.SMTPException as e:
            raise SmtpError(str(e)) from e

    def send_raw(
        self,
        from_addr: str,
        to_addrs: list[str],
        mime_string: str,
    ) -> None:
        if self._conn is None:
            raise SmtpError("Not connected.")
        try:
            self._conn.sendmail(from_addr, to_addrs, mime_string)
        except smtplib.SMTPException as e:
            raise SmtpError(str(e)) from e

    def __repr__(self) -> str:
        connected = self._conn is not None
        return f"SmtpClient(host={self.host!r}, port={self.port}, connected={connected})"


def message() -> EmailMessage:
    return EmailMessage()


def send_text(
    from_addr: str,
    to: str | list[str],
    subject: str,
    body: str,
    *,
    host: str,
    port: int = 587,
    username: str = "",
    password: str = "",
    use_tls: bool = True,
) -> None:
    recipients = [to] if isinstance(to, str) else to
    msg = (
        EmailMessage()
        .from_addr(from_addr)
        .subject(subject)
        .text(body)
    )
    for r in recipients:
        msg.to(r)
    with SmtpClient(host, port, username=username, password=password, use_tls=use_tls) as client:
        client.send(msg)


def send_html(
    from_addr: str,
    to: str | list[str],
    subject: str,
    html_body: str,
    text_body: str = "",
    *,
    host: str,
    port: int = 587,
    username: str = "",
    password: str = "",
    use_tls: bool = True,
) -> None:
    recipients = [to] if isinstance(to, str) else to
    msg = (
        EmailMessage()
        .from_addr(from_addr)
        .subject(subject)
        .html(html_body)
    )
    if text_body:
        msg.text(text_body)
    for r in recipients:
        msg.to(r)
    with SmtpClient(host, port, username=username, password=password, use_tls=use_tls) as client:
        client.send(msg)


if __name__ == "__main__":
    print("--- EmailMessage builder ---")
    msg = (
        EmailMessage()
        .from_addr("sender@example.com", "Sender Name")
        .to("alice@example.com", "bob@example.com")
        .cc("carol@example.com")
        .bcc("audit@example.com")
        .reply_to("noreply@example.com")
        .subject("Hello from smtp_utils")
        .text("Plain text body.")
        .html("<h1>Hello</h1><p>HTML body.</p>")
    )
    mime = msg.build()
    print("MIME type:", mime.get_content_type())
    print("From:    ", mime["From"])
    print("To:      ", mime["To"])
    print("Cc:      ", mime["Cc"])
    print("Subject: ", mime["Subject"])
    print("Parts:   ", [p.get_content_type() for p in mime.walk() if p.get_content_type() != mime.get_content_type()])

    print("\n--- text-only message ---")
    msg2 = EmailMessage().from_addr("a@b.com").to("c@d.com").subject("Hi").text("Hello!")
    mime2 = msg2.build()
    print("MIME type:", mime2.get_content_type())
    print("Payload preview:", mime2.as_string()[:80].replace("\n", " "))

    print("\n--- html-only message ---")
    msg3 = EmailMessage().from_addr("a@b.com").to("c@d.com").subject("Hi").html("<b>Bold</b>")
    mime3 = msg3.build()
    print("MIME type:", mime3.get_content_type())

    print("\n--- all_recipients ---")
    print("recipients:", msg.all_recipients())

    print("\n--- SmtpClient repr (not connected) ---")
    client = SmtpClient("smtp.example.com", 587, username="user", password="pass")
    print(client)

    print("\n--- message() factory ---")
    m = message().from_addr("x@y.com").to("z@w.com").subject("Test").text("body")
    print("built:", m.build().get_content_type())

    print("\n--- custom header ---")
    msg4 = (
        EmailMessage()
        .from_addr("a@b.com")
        .to("c@d.com")
        .subject("Custom")
        .text("body")
        .header("X-Priority", "1")
        .header("X-Mailer", "smtp_utils")
    )
    mime4 = msg4.build()
    print("X-Priority:", mime4["X-Priority"])
    print("X-Mailer:  ", mime4["X-Mailer"])

    print("\n--- send_text / send_html (no live server, just show SmtpError) ---")
    try:
        send_text("a@b.com", "c@d.com", "Hi", "Body", host="localhost", port=9999)
    except SmtpError as e:
        print(f"SmtpError (expected): {e}")
    except OSError as e:
        print(f"OSError (expected - no local SMTP): {type(e).__name__} errno={e.errno}")
