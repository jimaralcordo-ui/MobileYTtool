from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import yt_dlp


# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    template_folder=r"C:\Users\Amoe\Desktop\yt-tool\templates"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DOWNLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "downloads"
)

COOKIE_FILE = os.path.join(
    BASE_DIR,
    "cookies.txt"
)

os.makedirs(
    DOWNLOAD_FOLDER,
    exist_ok=True
)


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return render_template(
        "mobile_index.html"
    )


# ============================================================
# PROCESS YOUTUBE URL
# ============================================================

@app.route("/process", methods=["POST"])
def process():

    url = str(
        request.form.get(
            "url",
            ""
        )
    ).strip()

    if not url:

        return render_template(
            "mobile_index.html",
            error="Please enter a YouTube URL."
        )

    try:

        options = {

            "quiet": True,

            "no_warnings": True,

            "noplaylist": True,

            "cookiefile": COOKIE_FILE

        }

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        title = info.get(
            "title",
            "Unknown video"
        )

        return render_template(
            "mobile_video.html",
            title=title,
            url=url
        )

    except Exception as e:

        print(
            "PROCESS ERROR:"
        )

        print(
            repr(e)
        )

        return render_template(
            "mobile_index.html",
            error=str(e)
        )


# ============================================================
# DOWNLOAD WAIT PAGE
# ============================================================

@app.route("/wait", methods=["GET"])
def wait():

    url = request.args.get(
        "url",
        ""
    ).strip()

    quality = request.args.get(
        "quality",
        "720"
    )

    if not url:

        return render_template(
            "mobile_index.html",
            error="Missing YouTube URL."
        )

    return render_template(
        "mobile_wait.html",
        url=url,
        quality=quality
    )


# ============================================================
# DOWNLOAD
# ============================================================

@app.route("/download", methods=["POST"])
def download():

    url = request.form.get(
        "url",
        ""
    ).strip()

    quality = request.form.get(
        "quality",
        "720"
    )

    if not url:

        return jsonify({

            "error":
                "Missing YouTube URL"

        }), 400


    # --------------------------------------------------------
    # QUALITY
    # --------------------------------------------------------

    try:

        height = int(
            quality
        )

    except (
        ValueError,
        TypeError
    ):

        height = 720


    if height not in [
        360,
        480,
        720,
        1080
    ]:

        height = 720


    # --------------------------------------------------------
    # UNIQUE FILE
    # --------------------------------------------------------

    filename = str(
        uuid.uuid4()
    )

    output_template = os.path.join(

        DOWNLOAD_FOLDER,

        filename + ".%(ext)s"

    )


    # --------------------------------------------------------
    # YT-DLP OPTIONS
    # --------------------------------------------------------

    options = {

        "format":
            f"bestvideo[height<={height}][ext=mp4]+"
            f"bestaudio[ext=m4a]/"
            f"best[height<={height}][ext=mp4]/"
            f"best[height<={height}]/"
            "18",

        "outtmpl":
            output_template,

        "merge_output_format":
            "mp4",

        "noplaylist":
            True,

        "cookiefile":
            COOKIE_FILE,

        "quiet":
            False,

        "no_warnings":
            False

    }


    # --------------------------------------------------------
    # LOG
    # --------------------------------------------------------

    print(
        "========================================"
    )

    print(
        "MOBILE DOWNLOAD REQUEST"
    )

    print(
        "URL:",
        url
    )

    print(
        "QUALITY:",
        height
    )

    print(
        "COOKIE FILE:",
        COOKIE_FILE
    )

    print(
        "COOKIE EXISTS:",
        os.path.exists(
            COOKIE_FILE
        )
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    try:

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            ydl.download([
                url
            ])


        # ----------------------------------------------------
        # FIND DOWNLOADED FILE
        # ----------------------------------------------------

        files = [

            f

            for f in os.listdir(
                DOWNLOAD_FOLDER
            )

            if f.startswith(
                filename + "."
            )

        ]


        if not files:

            print(
                "OUTPUT FILE NOT FOUND"
            )

            return jsonify({

                "error":
                    "Downloaded file was not found."

            }), 500


        # ----------------------------------------------------
        # PREFER MP4
        # ----------------------------------------------------

        mp4_files = [

            f

            for f in files

            if f.lower().endswith(
                ".mp4"
            )

        ]


        if mp4_files:

            final_file = (
                mp4_files[0]
            )

        else:

            final_file = (
                files[0]
            )


        # ----------------------------------------------------
        # FULL PATH
        # ----------------------------------------------------

        filepath = os.path.join(

            DOWNLOAD_FOLDER,

            final_file

        )


        print(
            "FILE READY:",
            filepath
        )


        # ----------------------------------------------------
        # SEND FILE
        # ----------------------------------------------------

        return send_file(

            filepath,

            as_attachment=True,

            download_name="video.mp4"

        )


    except Exception as e:

        print(
            "========================================"
        )

        print(
            "MOBILE DOWNLOAD ERROR"
        )

        print(
            repr(e)
        )

        print(
            "========================================"
        )

        return jsonify({

            "error":
                str(e)

        }), 500


# ============================================================
# HEALTH
# ============================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status":
            "ok",

        "service":
            "YTTool Mobile",

        "templates":
            os.path.exists(
                os.path.join(
                    BASE_DIR,
                    "templates"
                )
            ),

        "mobile_index":
            os.path.exists(
                os.path.join(
                    BASE_DIR,
                    "templates",
                    "mobile_index.html"
                )
            )

    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "YTTOOL MOBILE SERVER"
    )

    print(
        "BASE DIR:",
        BASE_DIR
    )

    print(
        "TEMPLATE FOLDER:",
        os.path.join(
            BASE_DIR,
            "templates"
        )
    )

    print(
        "MOBILE INDEX EXISTS:",
        os.path.exists(
            os.path.join(
                BASE_DIR,
                "templates",
                "mobile_index.html"
            )
        )
    )

    print(
        "DOWNLOAD FOLDER:",
        DOWNLOAD_FOLDER
    )

    print(
        "========================================"
    )

    app.run(

        host="0.0.0.0",

        port=5002,

        debug=False

    )