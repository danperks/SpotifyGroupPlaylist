var SongsToVoteOn = [];
var VotesInFavour = [];
var VotesAgainst = [];
var CurrentSong = "";




var CurrentGroup = sessionStorage.getItem("CurrentGroup");
var CurrentName = sessionStorage.getItem("CurrentName");
var StateOfCheckbox = false;
var CurrentAudioTrack = "";
console.log(CurrentGroup);
$(document).ready(function() {
    document.getElementById("playlistCode").innerHTML = "Playlist Code: " + CurrentGroup;
    document.getElementById("playlistName").innerHTML = CurrentName;
    $.get('/ReturnSongsAwaitVote', { GroupId: CurrentGroup }).done(function(data) {
        SongsToVoteOn = [];
        CurrentSong = "";
        SongsToVoteOn = data;
        //console.log(data);
        //alert(SongsToVoteOn)
        NextSong();
        //console.log(SongsToVoteOn);
        //CheckBoxStateCheck();
    }).fail(function(data) {
        alert("Your Session Has Likely Expired  - Redirecting to group selection page");
        window.location.replace("/");
    });
});


function VoteInFavour() {
    if (StateOfCheckbox) {
        var GroupValueToSendBack = "ALL";
    } else {
        var GroupValueToSendBack = CurrentGroup;
    }
    console.log("Current Votes Applicable To " + GroupValueToSendBack.toString())
    $.get('/VotesReturned', { InFavourVotes: JSON.stringify([CurrentSong]), GroupId: GroupValueToSendBack }).done(function(data) {
        NextSong();
    })
}

function VoteAgainst() {
    if (StateOfCheckbox) {
        var GroupValueToSendBack = "ALL";
    } else {
        var GroupValueToSendBack = CurrentGroup;
    }
    console.log("Current Votes Applicable To " + GroupValueToSendBack.toString())
    $.get('/VotesReturned', { VotesAgainst: JSON.stringify([CurrentSong]), GroupId: GroupValueToSendBack }).done(function(data) {
        NextSong();
    })
}

function NextSong() {
    //console.log(SongsToVoteOn)
    $("#PreviewPlayer").hide();
    //console.log("Next Song Called");
    if (SongsToVoteOn && SongsToVoteOn.length > 0) {
        CurrentSong = SongsToVoteOn.pop();
        document.getElementById("VoteCount").innerHTML = String(SongsToVoteOn.length + 1);
        ifrm = document.getElementById("spotembed")
        ifrm.src = "https://open.spotify.com/embed/track/" + String(CurrentSong);
        ifrm.style.display = "block";
    } else {
        //Now at end of the list
        PackUpSendBack();
    }
    // console.log(SongsToVoteOnTwo)

}

function PackUpSendBack() {
    //alert("End Of List Reached");
    //HideElements();
    RefreshOutputPlaylist();
    alert("End of Songs - Check back later to see if any more songs have been submitted");
    document.getElementById("VoteCount").innerHTML = "0";
    document.getElementById("voteyes").style.display = "none";
    document.getElementById("voteno").style.display = "none";
    document.getElementById("spotembed").style.display = "none";
    // add the check to see if all votes have been received

}

function CheckBoxStateCheck() {
    StateOfCheckbox = document.getElementById("VotesPermanent").checked;
    //alert(StateOfCheckbox);
    console.log(StateOfCheckbox);
}

function HideElements() {
    $('#divHide').children().hide();

}

function ManualRefresh() {
    RefreshOutputPlaylist();
    alert("The playlist has been recreated and updated successfully!");
}

function RefreshOutputPlaylist() {
    $.get("/RefreshOutputPlaylist", { GroupId: CurrentGroup });
}


// Both Arrays combined into JSON String wdetailing what each array is
//field for group added
//field for user id added
//string sent back up to the flask
//string unpacked on the flask
//array of negative votes is then porcessed (simply just record each vote on the database)
//arrray of positive votes is then done in the same manner