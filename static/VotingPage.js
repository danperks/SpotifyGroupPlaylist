import cookies from 'js-cookie';
"use strict";
//jslint browser:true //

var SongsToVoteOn = [];
var VotesInFavour = [];
var VotesAgainst = [];
var CurrentSong = "";


var script = document.createElement('script');
script.src = 'https://code.jquery.com/jquery-3.4.1.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);


$(document).ready(function() {
    $.get('/ReturnSongsAwaitVote',{GroupId:"J9r9J30pwi"}).done(function(data){
        SongsToVoteOn= data;
        alert(SongsToVoteOn)
        NextSong();
                //console.log(SongsToVoteOn);
                
        MakeButtonsLive();
    });
});

function MakeButtonsLive(){//probably should mess around with doing this propelry off a chain of promises / async funcitons etc, but acc that seems to work so , even if sketchy
    console.log(SongsToVoteOn)
    
    console.log(CurrentSong)
    if (SongsToVoteOn.length >0){
        $("#AgainstButton").prop("disabled", false);
        $("#InFavourButton").prop("disabled", false);
        
        CurrentSong = SongsToVoteOn[0];
        //console.log(CurrentSong)
    }
}

function VoteInFavour(){
    alert("Vote In Favour" + CurrentSong);
    VotesInFavour.push(CurrentSong);
    NextSong();
    
}


function VoteAgainst(){
    
    alert("Vote Against" + CurrentSong);
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
        PackUpSendBack()
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
            console.log(response)
        }

    })
}
function PackUpSendBack(){
    alert("End Of List Reached")
    // Both Arrays combined into JSON String wdetailing what each array is
    //field for group added
    //field for user id added
    //string sent back up to the flask
    //string unpacked on the flask
    //array of negative votes is then porcessed (simply just record each vote on the database)
    //arrray of positive votes is then done in the same manner
}