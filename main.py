from pyrogram import Client, filters
import config
import sqlite3

connection = sqlite3.connect('file_list.db')
cursor = connection.cursor()

app = Client(
	"fileStorageBot",
	bot_token=config.BOT_TOKEN,
	api_id=config.API_ID,
	api_hash=config.API_HASH
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await client.send_message(message.chat.id, f"""**Hoşgeldin.**
**Sohbet:** <b>{message.chat.title}</b>
**Sohbet ID:** <code>{message.chat.id}</code>
**Kullanıcı ID:** <code>{message.from_user.id}</code>

**Kullanım:**
/search <dosya> - Dosyayı veritabanında arat.
/add - Veritabanına dosya gönder.
/list - Veritabanındaki dosyaları listeler.
/admincmd - Admin komutlarını listeler (Admin olmalısınız.)
""")
    
@app.on_message(filters.command("get"))
async def get_file_id(client, message):
    try:
        await client.send_message(message.chat.id, f"""
<code>{message.reply_to_message.document.file_id}</code>
""")
    except:
        await client.send_message(message.chat.id, "[-] Hata! Lütfen bir dosyaya veya dökümana yanıt verin!")
    #await app.send_document(message.chat.id, f"{message.reply_to_message.document.file_id}", caption="document caption")


@app.on_message(filters.command("search"))
async def search(client, message):
    try:
        file_name = f"{message.command[1]}"
        cursor.execute("SELECT file_id FROM file_list WHERE file_name LIKE ?", ('%' + file_name + '%',))
        result = cursor.fetchall()
        if result:
            file_id = result
            for item in result:
                await client.send_document(message.chat.id, item[0])
        else:
            await client.send_message(message.chat.id, "[-] Belirtilen dosya bulunamadı.")
    except IndexError:
        await client.send_message(message.chat.id, f"""
[-] Lütfen aramak için bir terim girin.

**Kullanım:**
/search dosya_adı
""")
        
@app.on_message(filters.command("add"))
async def add(client, message):
    try:
        file_name = f"{message.reply_to_message.document.file_name}"
        file_id = f"{message.reply_to_message.document.file_id}"
        try:
            cursor.execute("INSERT INTO file_list (file_name, file_id) VALUES (?, ?)", (f"{file_name}", f"{file_id}"))
            await client.send_message(message.chat.id, "[i] Dosya veritabanına başarıyla eklendi.")
        except:
            await client.send_message(message.chat.id, "[-] Dosya veritabanına eklenirken bir sorun oluştu.")
    except AttributeError:
        await client.send_message(message.chat.id, "[-] Lütfen bir dosyaya yanıt verin.")

@app.on_message(filters.command("db"))
async def db(client, message):
    adminConnection = sqlite3.connect('admins.db')
    cursor = adminConnection.cursor()
    check_user_id = f"{message.from_user.id}"
    query = "SELECT * FROM admin_list WHERE user_id = ?"
    cursor.execute(query, (check_user_id,))
    if cursor.fetchone():
        try:
            await client.send_document(message.chat.id, "file_list.db")
        except:
            await client.send_message(message.chat.id, "[-] Hata! Bilinmeyen bir sebepten ötürü veritabanı dosyası yüklenemedi!")
    else:
        await client.send_message(message.chat.id, "[-] Hata! Admin listesinde olmadığınız için bu dosyayı alamazsınız.")

@app.on_message(filters.command("list"))
async def list(client, message):
    STATIC_SQL_COMMAND = "SELECT file_name FROM file_list"
    cursor.execute(STATIC_SQL_COMMAND)
    results = cursor.fetchall()
    msg_text = """
"""
    for single_file in results:
        msg_text += str(single_file[0]) + '\n'
    await client.send_message(message.chat.id, "<b>Bottaki mevcut dosyalar:</b>" + "\n" + msg_text)

@app.on_message(filters.command("admincmd"))
async def admincmd(client, message):
    adminConnection = sqlite3.connect('admins.db')
    cursor = adminConnection.cursor()
    check_user_id = f"{message.from_user.id}"
    query = "SELECT * FROM admin_list WHERE user_id = ?"
    cursor.execute(query, (check_user_id,))
    if cursor.fetchone():
        try:
            await client.send_message(message.chat.id, f"""
<b>Admin Komutları</b>

/db - Veritabanı dosyasını gönderir.
""")
        except:
            await client.send_message(message.chat.id, "[-] Bir hata oluştu!")
    else:
        await client.send_message(message.chat.id, "[-] Hata! Admin listesinde olmadığınız için bu komutu çalıştıramazsınız.")

app.run()