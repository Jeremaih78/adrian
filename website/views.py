from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
    )
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django import forms


from .forms import SignUpForm
from .models import Album, Song
from .forms import NewAlbum, NewSong

########################################################
from django.shortcuts import render
from django.core.mail import send_mail

def home(request):
    albums = Album.objects.all()
    return render(request, 'dentist/home.html',{'albums':albums})

def videos(request):
    
    return render(request, 'dentist/videos.html',{})




##########################################################################

def contact(request):
    if request.method == "POST":
        Name = request.POST['Name']
        Phone = request.POST['Phone']
        Email = request.POST['Email']
        Message = request.POST['Message']
        return render(request, 'dentist/contact.html',{'Name': Name})

        #send mail
        send_mail(
            subject, #subject
            message,  #message
            Email, #from email
            ['adriannzvimbo@gmail.com','a.aaronsavanna@gmail.com'], #tto email
        )
    else:
        return render(request, 'dentist/contact.html',{})

##########################################################################   
def signup(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dentist:home')
        else:
            message = 'Looks like a username with that email or password already exists'
            return render(request, 'dentist/user_signup.html', {'form':form,'message':message})
    else:
        form = SignUpForm()
        return render(request, 'dentist/user_signup.html', {'form':form})

###############################################################
def profile_detail(request, username):
    # show all albums of the artist
    albums = get_object_or_404(User, username=username)
    albums = albums.albums.all()
    return render(request, 'dentist/artist_information.html', {'albums':albums, 'username':username})

#........................................................#

@login_required
def add_album(request, username):
    user = get_object_or_404(User, username=username)
    #only currently logged in user can add album else will be redirected to home
    if user == request.user:
        if request.method == 'POST':
            form = NewAlbum(request.POST, request.FILES)
            if form.is_valid():
                # form.save(commit='False')
                album = Album.objects.create(
                    album_logo=form.cleaned_data.get('album_logo'),
                    album_name=form.cleaned_data.get('album_name'),
                    album_genre=form.cleaned_data.get('album_genre'),
                    uploaded_on = timezone.now(),
                    album_artist = request.user
                )
                return redirect('dentist:profile_detail', username=request.user)
        else:
            form = NewAlbum()
        return render(request, 'dentist/create_new_album.html', {'form':form})
    else:
        return redirect('dentist:profile_detail', username=user)

#........................................................#

def album_detail(request,username, album):
    #show album details here. single album's details.
    album = get_object_or_404(Album, album_name=album)
    songs = get_object_or_404(User, username=username)
    songs = songs.albums.get(album_name=str(album))
    songs = songs.songs.all()
    return render(request, 'dentist/album_information.html', {'songs':songs, 'album':album, 'username':username
    })

#........................................................#


#........................................................#

@login_required
def delete_album(request, username, album):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        album_to_delete = get_object_or_404(User, username=username)
        album_to_delete = album_to_delete.albums.get(album_name=album)
        song_to_delete = album_to_delete.songs.all()
        for song in song_to_delete:
            song.delete_media()#deletes the song_file
        album_to_delete.delete_media()#deletes the album_logo
        album_to_delete.delete()#deletes the album from database
        return redirect('dentist:profile_detail', username=username)
    else:
        return redirect('dentist:profile_detail', username=username)

#........................................................#

@login_required
def add_song(request, username, album):

    user = get_object_or_404(User, username=username)

    if request.user == user:

        album_get = Album.objects.get(album_name=album)

        if request.method == 'POST':
            form = NewSong(request.POST, request.FILES)
            if form.is_valid():
                # form.save(commit='False')
                song = Song.objects.create(
                    song_name = form.cleaned_data.get('song_name'),
                    song_file = form.cleaned_data.get('song_file'),
                    song_album = album_get
                )
                return redirect('dentist:album_detail', username=username, album=album)

        else:
            form = NewSong()
            return render(request, 'dentist/create_new_song.html', {'form':form})
    else:
        return redirect('dentist:album_detail', username=username, album=album)
