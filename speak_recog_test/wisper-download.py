import whisper
whisper.load_model("base")  # Downloads the model for offline use

# Model	    Size	    Accuracy	    Speed	         Best For
# tiny	    39 MB	    Low	            🔥 Fastest	    Low-resource devices
# base	    74 MB	    Moderate	    ⚡ Fast	       General use, small apps
# small	    244 MB	    Good	        🚀 Medium	    Good balance of speed & accuracy
# medium	769 MB	    Better	        🏎️ Slower	     High accuracy, good for accents
# large	    1.55 GB	    Best	        🐢 Slowest	    Most accurate, multilingual