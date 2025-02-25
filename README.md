# SkyDrop

<img src="static/src/SkyDropICON.png" height="200">

# What is this?

SkyDrop is an open source, lightweight, cross platform AirDrop server.

It takes a URL request, gathers the contents, and hosts it on the index page for easy copying and sharing.

The code is designed to only hold the most recent TEN items for both files and text.

SkyDrop is best used with the iOS Shortcut, which you can find below.

# ❗ Watch the Demo video on Youtube
<a href="https://www.youtube.com/watch?v=SV0vZcAXVro" target="_blank">
  <img src="static/src/skydropVid.png" width="560" height="315" />
</a>


# Usage

## Setting Up the Server

To set up the server, you need a computer that is always running on the same IP Address/URL. A Raspberry Pi works best for this, but you can also use PythonAnywhere or AWS. I will be providing instructions for the Raspberry Pi Only.

#### Setting up the Pi
1. You need to either:
   1.  Make sure your raspberry pi has a **Static IP Address**
   2.  Use a CloudFlare Tunnel to securely pipe your localhost to a URL
2. Install Python & pip
3. Use pip to install Flask
4. Create ```key.txt```, and use the following format for your login details. Replace ```key_for_flask_login``` with any string, an example being ```394848329292983848939392929383483```
```
login:password
key_for_flask_login
```
5. Open a terminal and run ```python receiver.py```
6. Leave the terminal running, this is your server, and should remain active at all times

Done! Now, we can move onto the iOS Shortcut

## Setting up the iOS Shortcut
1. [Download the Shortcut to your iPhone](https://www.icloud.com/shortcuts/beb1a4544f67442f98d4582a6d78f0bd)
2. Open the shortcut and edit the **text** option near the top to attatch to your URL. Something like **http://```192.168.1.1:5000```/receive** for example
3. Edit the Username & Password to the ones you set in ```key.txt```
4. Add it to your Share Sheet
5. Add it to your home screen

Done! You should now be all set up and ready to airdrop!

# Tips
1. Keep the URL to the index page bookmarked on your browser
2. Move the Share Sheet option to the top by clicking ```Edit Actions...``` on the bottom of your share sheet

# ⚠️ Important ⚠️
### Keep your login & password ```PRIVATE```

# No iPhone?

1. Feel free to create a version that mimics the iOS Shortcut. The important part of it is that it sends a URL Request that includes the correct headers and requests.
   Create a pull request with said version if you make one!
