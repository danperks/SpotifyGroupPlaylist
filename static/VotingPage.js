"use strict";
//jslint browser:true //

var SongsToVoteOn = [];
var VotesInFavour = [];
var VotesAgainst = [];
var CurrentSong = "";




var CurrentGroup = sessionStorage.getItem("CurrentGroup");
$(document).ready(function() {
    $.get('/ReturnSongsAwaitVote',{GroupId:CurrentGroup}).done(function(data){
        SongsToVoteOn= data;
        //alert(SongsToVoteOn)
        NextSong();
                //console.log(SongsToVoteOn);
        
        MakeButtonsLive();
    });
});

function MakeButtonsLive(){//probably should mess around with doing this propelry off a chain of promises / async funcitons etc, but acc that seems to work so , even if sketchy
    if (SongsToVoteOn.length >0){
        $("#AgainstButton").prop("disabled", false);
        $("#InFavourButton").prop("disabled", false);
        //alert(sessionStorage.getItem("CurrentGroup"));
        CurrentSong = SongsToVoteOn[0];
        //console.log(CurrentSong)
    }
}

function VoteInFavour(){
    //alert("Vote In Favour" + CurrentSong);
    VotesInFavour.push(CurrentSong);
    NextSong();

    
}


function VoteAgainst(){
    //alert("Vote Against" + CurrentSong);
    VotesAgainst.push(CurrentSong);
    NextSong();
}
function NextSong(){
    //console.log("Next Song Called");
    if (SongsToVoteOn && SongsToVoteOn.length){
        CurrentSong = SongsToVoteOn.pop();
        SetAlbumImage(CurrentSong);
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
function PackUpSendBack(){
    alert("End Of List Reached");
    console.log(JSON.parse(VotesInFavour));
    // Both Arrays combined into JSON String wdetailing what each array is
    //field for group added
    //field for user id added
    //string sent back up to the flask
    //string unpacked on the flask
    //array of negative votes is then porcessed (simply just record each vote on the database)
    //arrray of positive votes is then done in the same manner
}