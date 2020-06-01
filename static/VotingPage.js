"use strict";
//jslint browser:true //

var SongsToVoteOn = [];
var VotesInFavour = [];
var VotesAgainst = [];
var CurrentSong = "";




var CurrentGroup = sessionStorage.getItem("CurrentGroup");
var StateOfCheckbox = false;
var CurrentAudioTrack = "";
console.log(CurrentGroup);
$(document).ready(function() {
    $.get('/ReturnSongsAwaitVote',{GroupId:CurrentGroup}).done(function(data){
        SongsToVoteOn=[];
        CurrentSong = "";
        SongsToVoteOn= data;
        //console.log(data);
        //alert(SongsToVoteOn)
        NextSong();
                //console.log(SongsToVoteOn);
        MakeButtonsLive();
        CheckBoxStateCheck();
    });
});

function MakeButtonsLive(){//probably should mess around with doing this propelry off a chain of promises / async funcitons etc, but acc that seems to work so , even if sketchy
    if (SongsToVoteOn.length >0){
        document.getElementById("AgainstButton").hidden = false;
        document.getElementById("InFavourButton").hidden = false;
        $("#AgainstButton").removeAttr("disabled");
        $("#InFavourButton").removeAttr("disabled");
         //,false);
        //$("#InFavourButton").prop("disabled",false);
        //alert(sessionStorage.getItem("CurrentGroup"));
        
        //console.log(CurrentSong)
    }
}

function VoteInFavour(){
    if(StateOfCheckbox){
        var GroupValueToSendBack = "ALL";
    }
    else{
        var GroupValueToSendBack = CurrentGroup;
    }
    console.log("Current Votes Applicable To " + GroupValueToSendBack.toString())
    $.get('/VotesReturned',{InFavourVotes:JSON.stringify([CurrentSong]),GroupId:GroupValueToSendBack}).done(function(data){
        NextSong();
    })
}

    



function VoteAgainst(){
    if(StateOfCheckbox){
        var GroupValueToSendBack = "ALL";
    }
    else{
        var GroupValueToSendBack = CurrentGroup;
    }
    console.log("Current Votes Applicable To " + GroupValueToSendBack.toString())
    document.getElementById("PreviewPlayer").pause();
    $.get('/VotesReturned',{VotesAgainst:JSON.stringify([CurrentSong]),GroupId:GroupValueToSendBack}).done(function(data){
        NextSong();
    })
}
function NextSong(){
    //console.log(SongsToVoteOn)
    $("#PreviewPlayer").hide();
    //console.log("Next Song Called");
    if (SongsToVoteOn && SongsToVoteOn.length >0){
        CurrentSong = SongsToVoteOn.pop();
        document.getElementById("VoteCount").innerHTML = String(SongsToVoteOn.length);
        SetAlbumImage(CurrentSong);
        GetThirtySecondAudio(CurrentSong);
    }
    else{
        //Now at end of the list
        PackUpSendBack();
    }
    // console.log(SongsToVoteOnTwo)
    
}
function SetAlbumImage(SongID){
    $.ajax({
        url:"https://api.spotify.com/v1/tracks/"+ String(SongID),
        headers:{
            'Authorization': 'Bearer ' + String(Cookies.get("AuthToken")),
        },
        success:function(response){
            document.getElementById("AlbumCover").src = response["album"]["images"][0]["url"];
            document.getElementById("Artist").innerHTML = response["artists"][0]["name"];// will only get first artist but you know where to go with that
            document.getElementById("Title").innerHTML = response["name"]
           // alert(Cookies.get("AuthToken"))
        }

    })
}
function GetThirtySecondAudio(SongID){
    $.ajax({
        url:"https://api.spotify.com/v1/tracks/"+ String(SongID)+"?market=from_token",
        headers:{
            'Authorization': 'Bearer ' + String(Cookies.get("AuthToken")),
        },
        success:function(response){
            console.log(response)
            CurrentAudioTrack = response["preview_url"]
            if(CurrentAudioTrack == null){
                $("#PreviewPlayer").hide();
            }
            else{
                $("#PreviewPlayer").show();
                document.getElementById("PreviewPlayer").src = CurrentAudioTrack;
            }
        }

        })
           
           // alert(Cookies.get("AuthToken"))
        }

    


function PackUpSendBack(){
    //alert("End Of List Reached");
    HideElements();
    RefreshOutputPlaylist();
    alert("End of Songs - Check back later to see if any more songs have been submitted");
    // add the check to see if all votes have been received
     
}
function CheckBoxStateCheck(){
    StateOfCheckbox = document.getElementById("VotesPermanent").checked;
    //alert(StateOfCheckbox);
    console.log(StateOfCheckbox);
}
function HideElements(){
    $('#divHide').children().hide();
    
}

function RefreshOutputPlaylist(){
    $.get("/RefreshOutputPlaylist",{GroupId:CurrentGroup}).done(function(){
        console.log("Output Playlist Refreshed");
    })
}


    // Both Arrays combined into JSON String wdetailing what each array is
    //field for group added
    //field for user id added
    //string sent back up to the flask
    //string unpacked on the flask
    //array of negative votes is then porcessed (simply just record each vote on the database)
    //arrray of positive votes is then done in the same manner
