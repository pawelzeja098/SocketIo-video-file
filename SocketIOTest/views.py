"""
Routes and views for the flask application.
"""

from datetime import datetime
import os.path
from flask import render_template, request
# from SocketIOTest import app
from SocketIOTest.VideoControlerClass import VideoControler
from SocketIOTest.TrascriptionWhisper.TranscriptionControllerClass import TranscriptionController
import SocketIOTest.globaldata as GD
import os
# @app.route('/')
# @app.route('/home')
# def home():
#     """Renders the home page."""
#     return render_template(
#         'index.html',
#         title='Home Page',
#         year=datetime.now().year,
#     )

def init_routes(app,socketio):

    GD.socketio = socketio



    @app.route('/video_catalogue')
    def video_catalogue():
        """Renders the video catalogue page"""
        files = os.listdir(f"{GD.folder_path}")
    
        files_mp4 = [f for f in files if f.endswith("mp4")]
        files_csv = [f for f in files if f.endswith("csv")]

        files_onlymp4 = [{"video": f} for f in files_mp4 if not f.replace(".mp4", ".csv") in files_csv]        

        files = files_onlymp4
        files.extend([{"video": f, "txt_csv": f.replace(".mp4", ".csv")} for f in files_mp4 if f.replace(".mp4", ".csv") in files_csv])

        # files = [{"video": f} for f in files_mp4]
        return render_template(
            'video_catalogue.html',
            title='Video Catalogue',
            year=datetime.now().year,
            files = files
        )

    @app.route('/file-upload',methods=["POST"])
    def file_upload():
        files = []
        for i in range(len(request.files)):

            files.append(request.files.getlist(f'file[{i}]'))
            

        a = 0

    @app.route("/viewer")
    def viewer():
        

        
        if 'video' in request.args:
            video = request.args.get('video')

        if 'txt_csv' in request.args:            
            txt_csv = request.args.get('txt_csv')


        return render_template(
            "index.html",
            title="Video Viewer",
            year=datetime.now().year,
            message="Video Viewer",
            video=video
        )


    @app.route('/contact')
    def contact():
        """Renders the contact page."""
        return render_template(
            'contact.html',
            title='Contact',
            year=datetime.now().year,
            message='Your contact page.'
        )

    @app.route('/about')
    def about():
        """Renders the about page."""
        return render_template(
            'about.html',
            title='About',
            year=datetime.now().year,
            message='Your application description page.'
        )


    @app.route('/')
    @app.route('/home')
    def home():
        """Render the index.html template on the root URL."""
        return render_template('index.html')


    @socketio.on("start")
    def handle_start(data):
        print(" Command: START")
        # filepath = "E:/Programowanie/MOV2024.mp4"
        
        filepath = data.get("video")

        video_path = os.path.join(GD.folder_path,filepath)

        
        if GD.th is not None:
            if GD.th.name == video_path:
                GD.th.handle_start_stop(True)
                return
            GD.th.handle_start_stop(False)
            GD.th.running = False

        
    
        GD.th = VideoControler(video_path,GD.socketio)

        GD.th.handle_start_stop(True)
        # GD.th.handle_start_stop(play=True)
        

    @socketio.on("stop")
    def handle_stop(data):
        print(" Command: STOP")
        GD.th.handle_start_stop(play=False)
        socketio.emit("status", {"message": "Streaming stopped"})


    @socketio.on("rewind")
    def handle_rewind(data):
        print("Command: REWIND")
    
        if GD.th is not None:
            #GD.th.handle_start_stop(False)
            
            time = int(data["time"])
            GD.th.CurrentTime=time  #  cap.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
            GD.th.subtitles.search_for_sub_idx(time)
            GD.th.socketio.emit("status", {"message": f"Rewinding video to {time}s"})
        # app.video_controller.subtitles.search_for_sub_idx(time)
    
        # app.video_controller.cap.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
   
    
        socketio.emit("status", {"message": f"Rewinding video to {time}s"})

    @socketio.on("trim_video")
    def handle_trim(data):
        print("Command: TRIM VIDEO")
    
        start_value = int(float(data['valueLow']))
        stop_value = int(float(data['valueUp']))
        GD.th.trim_start_value = start_value
        GD.th.trim_stop_value = stop_value
        trimmed_sub = GD.th.subtitles.get_trimmed_subtitles(start_value,stop_value)
        socketio.emit("trimmed_subtitles", {"subtitles": trimmed_sub})
        GD.th.trim_video()


    @socketio.on("start_transcription")
    def handle_transcription(data):
        print("Command: START TRANSCRIPTION")
    
        videoFile = data['VideoFile']

        tc = TranscriptionController(videoFile)
       
        # GD.th.trim_start_value = start_value
        # GD.th.trim_stop_value = stop_value
        # trimmed_sub = GD.th.subtitles.get_trimmed_subtitles(start_value,stop_value)
        # socketio.emit("trimmed_subtitles", {"subtitles": trimmed_sub})
        # GD.th.trim_video()