
from cmath import pi
import requests
import os
import cv2
import numpy as np
import webbrowser
import bpy
import base64

CLIENT_ID = "56651af3c4134034b9977c0a650b2cdf"
CLIENT_SECRET = "ba05f9e81dbc4443857aa9f3afcfc88b"
REDIRECT_URL = "http://127.0.0.1:5555/callback.html"

# DO NOT PUSH WHEN USER_CODE AND access_token_user IS NOT ""!!!
user_code = ""
access_token_user = "BQCXG7EaX2gQFx9R2MEdIjNxQxnfITbUcdk0MoQK9AbhjQZRQsQUWvfiF_4F5CbIl559XYGmp6lcCnWDk_dHKQsSZYl4p0cxzfNErYhIKFukJGC7poFz5aXkSryy_MiBDaTPlyG0lhcKIuT1tu9lRiFWVR8UcSPxr-FYxiucnm1x8Q"

AUTH_URL = "https://accounts.spotify.com/api/token"
CLIENT_AUTH_URL = "https://accounts.spotify.com/authorize"
BASE_URL = "https://api.spotify.com/v1/"

COVER_SIZE = 1.2  # size of the total cover
# distance between the color components until a new material is created
COVER_POSITION = (-2.6819, 1.10, 3.34549)

PIXEL_LEVEL = 0.01
WAIT_TIME = 5.0


song_id = ""
# get access token
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# Opens login screen -> After redirect, you can see the code. (Live Server must be active!)
# This code goes into "USER_CODE"


def requestAuthorization():
    url = CLIENT_AUTH_URL
    url += "?client_id=" + CLIENT_ID
    url += "&response_type=code"
    url += "&redirect_uri=" + REDIRECT_URL
    url += "&show_dialog=true"
    url += "&scope=user-read-currently-playing user-read-playback-position user-read-playback-state"
    webbrowser.open(url, new=0, autoraise=True)


# Gets the access token from the user code from the function above
# This code automatically gets stored in "access_token_user" and is needed for anything that has to do with user activity

def getAccessToken():
    encoded = base64.b64encode(
        (CLIENT_ID + ":" + CLIENT_SECRET).encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post(
        url="https://accounts.spotify.com/api/token",
        data={
            "code": user_code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://127.0.0.1:5555/callback.html"
        },
        headers=headers,
        json=True
    )
    access_token_user = r.json().get("access_token")
    print(access_token_user)

# Gets playback state of current device, if true, something is playing

def getCurPlaybackState():
    curPlayingUrl = BASE_URL + "me/player"
    header = {
        'Authorization': f'Bearer {access_token_user}'.format(token=access_token)
    }
    r = requests.get(url=curPlayingUrl, headers=header)
    respJson = r.json()

    return respJson["is_playing"]

# Returns the milliseconds that have passed since the song began

def getMsIntoCurSong(): 
    curPlayingUrl = BASE_URL + "me/player"
    header = {
        'Authorization': f'Bearer {access_token_user}'.format(token=access_token)
    }
    r = requests.get(url=curPlayingUrl, headers=header)
    respJson = r.json()

    return respJson["progress_ms"]


# Returns the percentage of how much the song is over

def getProgressIntoCurSong(): 

    max_length = getCurrentlyPlayedSong()["duration"]
    cur_position = getMsIntoCurSong()
    return((cur_position / max_length) * 100)


# Returns an object containing information about the currently played song

def getCurrentlyPlayedSong():
    curPlayingUrl = BASE_URL + "me/player/currently-playing"
    header = {
        'Authorization': f'Bearer {access_token_user}'.format(token=access_token)
    }
    r = requests.get(url=curPlayingUrl, headers=header)
    respJson = r.json()

    track_id = respJson["item"]["id"]
    track_name = respJson["item"]["name"]
    artists = respJson["item"]["artists"]
    artists_names = ", ".join([artist["name"] for artist in artists])
    duration = respJson["item"]["duration_ms"]
    link = respJson["item"]["external_urls"]["spotify"]

    currentTrackInfo = {
        "id": track_id,
        "name": track_name,
        "artists": artists_names,
        "duration": duration,
        "link": link
    }
    return currentTrackInfo

# Gets artist and name of current song in this format:
# "artist, artist2 - song"

def getArtistAndNameOfCurSong(): 
    currentTrackInfo = getCurrentlyPlayedSong()
    return currentTrackInfo["artists"] + " - " + currentTrackInfo["name"]

# Gets the artist image of the current song

def getArtistImage(track_id):
    track_req = requests.get(BASE_URL + "tracks/" + track_id, headers=headers)
    track_data = track_req.json()
    artist_id  = track_data["artists"][0]["id"]

    artist_req = requests.get(BASE_URL + "artists/" + artist_id, headers=headers)
    artist_data = artist_req.json()
    image = requests.get(artist_data["images"][0])
    img_string = np.frombuffer(image.content, np.uint8)
    img = cv2.imdecode(img_string, cv2.IMREAD_UNCHANGED)
    return img

# Gets the users profile image

def getLinkToCurUserImage():
    userUrl = BASE_URL + "me"
    header = {
        'Authorization': f'Bearer {access_token_user}'.format(token=access_token)
    }
    r = requests.get(url=userUrl, headers=header)
    respJson = r.json()
    image = requests.get(respJson["images"][0]["url"])
    img_string = np.frombuffer(image.content, np.uint8)
    img = cv2.imdecode(img_string, cv2.IMREAD_UNCHANGED)
    return img


# Gets cover of current song

def getCoverOfCurrentSong():
    currentTrackId = getCurrentlyPlayedSong()["id"]
    getSongImage(currentTrackId)


# Gets song from track id

def getSong(track_id):
    r = requests.get(BASE_URL + "tracks/" + track_id, headers=headers)
    d = r.json()

    artist = d["artists"][0]["name"]
    track = d["name"]
    print(artist, "-", track)
    print()


# Gets cover from track id

def getSongImage(track_id):
    getSong(track_id)
    r = requests.get(BASE_URL + "tracks/" + track_id, headers=headers)
    d = r.json()

    # Get image part
    cover_image = requests.get(d["album"]["images"][0]['url'])
    img_string = np.frombuffer(cover_image.content, np.uint8)
    img = cv2.imdecode(img_string, cv2.IMREAD_UNCHANGED)
    create_cover_from_image(img)

    # Show pixeled cover image
    """resized = cv2.resize(img, (100, 100), interpolation=cv2.INTER_NEAREST)
    cv2.namedWindow('img', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('img', 500, 500)
    cv2.imshow('img', resized)
    cv2.waitKey(0)"""


# Gets all albums from artist | test function, could be removed?

def getArtistsAlbums(artist_id):

    r = requests.get(BASE_URL + "artists/" + artist_id,
                     headers=headers)
    a = r.json()

    print("--- All Albums by the Artist '" + a["name"] + "' ---")

    r = requests.get(BASE_URL + "artists/" + artist_id + "/albums",
                     headers=headers,
                     params={"include_groups": "album", "limit": 50})
    d = r.json()

    albums = []
    for album in d["items"]:
        album_name = album["name"]

        trim_name = album_name.split('(')[0].strip()  # Filter out duplicates
        if trim_name.upper() in albums:
            continue

        albums.append(trim_name.upper())

        print(album_name, "---", album["release_date"])

    print()


# Loop that checks if the song has changed

def updateCurrentSong():
    global song_id 
  
    song_info = getCurrentlyPlayedSong()
    if song_info["id"] != song_id:
        song_id = song_info["id"]
        clear_console()
        print("--- Now Playing ---")
        getSong(song_id)
        return True
    return False
        
def update_cover(): 
    delete_current_cover()
    getCoverOfCurrentSong()

def delete_current_cover():
    bpy.ops.object.select_all(action='DESELECT')
    cover = bpy.context.scene.objects.get('cover')
    if cover:
        bpy.data.objects['cover'].select_set(True)
        bpy.ops.object.delete()
# Creates cover from image retrieved in getSongImage()

def generate_collection(): 
    collection = bpy.data.collections.new("Leuchtbilder")
    bpy.context.scene.collection.children["Leuchtbildtafel"].children.link(
        collection)

def create_cover_from_image(img):
    global COVER_SIZE
    global COVER_POSITION

    

    layer_collection = bpy.context.view_layer.layer_collection.children[
        "Leuchtbildtafel"].children["Leuchtbilder"]
    bpy.context.view_layer.active_layer_collection = layer_collection

    bpy.ops.mesh.primitive_plane_add(
        size=COVER_SIZE, location=COVER_POSITION, rotation=(pi/2, 0, pi))

    cover_object: bpy.types.Object = bpy.data.objects["Plane"]

    mat = create_cover_material(img)
    cover_object.data.materials.append(mat)
    cover_object.name = "cover"


def create_cover_material(cover_img):
    global COVER_SIZE
    global PIXEL_LEVEL
    mat: bpy.types.Material = bpy.data.materials.new("mat_Cover")
    mat.use_nodes = True
    node_tree: bpy.types.NodeTree = mat.node_tree

    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[20].default_value = 4
    tex_image = node_tree.nodes.new('ShaderNodeTexImage')

    rgba = cv2.cvtColor(cover_img, cv2.COLOR_RGB2BGRA)
    rows, cols, _ = cover_img.shape
    reversed_y = rgba[::-1]
    l = reversed_y.reshape(-2)
    list_pixel = l.tolist()
    pxl = [i/255 for i in list_pixel]
    img = bpy.data.images.new(
        "cover image", width=rows, height=cols)
    img.pixels.foreach_set(pxl)
    tex_image.image = img

    node_tree.links.new(
        bsdf.inputs['Base Color'], tex_image.outputs['Color'])
    vcector_math = node_tree.nodes.new('ShaderNodeVectorMath')
    node_tree.links.new(
        tex_image.inputs['Vector'], vcector_math.outputs['Vector'])
    vcector_math.operation = 'SNAP'

    vcector_math.inputs[1].default_value[0] = PIXEL_LEVEL
    vcector_math.inputs[1].default_value[1] = PIXEL_LEVEL
    vcector_math.inputs[1].default_value[2] = PIXEL_LEVEL

    tex_coordinates = node_tree.nodes.new('ShaderNodeTexCoord')
    node_tree.links.new(
        vcector_math.inputs['Vector'], tex_coordinates.outputs['Generated'])
    node_tree.links.new(
        bsdf.inputs['Emission'], tex_image.outputs['Color'])
    return mat

# Clears console
def clear_environment(): 
     # Select all objects
    bpy.ops.object.select_all(action='SELECT')
    # Delete the selected Objects
    bpy.ops.object.delete(use_global=False, confirm=False)
    # Delete mesh-data
    bpy.ops.outliner.orphans_purge()
    # Delete materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material, do_unlink=True)

def clear_console():
    os.system('cls')
   


def run_every_n_second():
    global WAIT_TIME
    global counter
    global TEST_SONG_COVERS
   
    is_new_song = updateCurrentSong()
    if is_new_song: 
        update_cover()
    #counter += 1
    return WAIT_TIME   

# import assets for the environment


def create_environment():
    bpy.ops.wm.open_mainfile(filepath="DAVT_Project_Scene.blend")
    """ skyscraper_degree = 90
    skyscraper_scale = 6
    bpy.data.objects["skyscraper"].rotation_euler[2] = skyscraper_degree * pi / 180
    bpy.data.objects["skyscraper"].location[2] *= skyscraper_scale
    for i in range(3):
        bpy.data.objects["skyscraper"].scale[i] = skyscraper_scale """


if (__name__ == "__main__"):
    # clear()
    # clear_environment() 
    # create_environment()
    # generate_collection()
    # requestAuthorization()
    # getAccessToken()
    # getSong("3I2Jrz7wTJTVZ9fZ6V3rQx")
    # getArtistsAlbums("26T3LtbuGT1Fu9m0eRq5X3")
    # getSongImage("3I2Jrz7wTJTVZ9fZ6V3rQx")
    # getArtistAndNameOfCurSong()
    # getArtistImage("50lTDu2BnjyqWnUFsxMryJ")
    # getLinkToCurUserImage()
    # getCurPlaybackState()
    # getMsIntoCurSong()
    # getProgressIntoCurSong()
    # getCoverOfCurrentSong()
    # getCurrentlyPlayedSong()
    # updateCurrentSong()
    # bpy.app.timers.register(run_every_n_second)