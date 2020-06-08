var PlaylistChoices = [];

function PlaylistBoxLoad(){
    document.getElementById("SubmissionOverlay").style.display = "block";
    LoadUserPlaylists();
}
function CloseBox(){
    document.getElementById("SubmissionOverlay").style.display = "none";

}
window.onclick = function(event){
    if(event.target == document.getElementById("SubmissionOverlay")){
        document.getElementById("SubmissionOverlay").style.display="none";
    }
}


function LoadUserPlaylistURLController(URL){
    URL = URL;
    while(URL != null){    
        if(URL == null){
            console.log("URL is NUll");
            break;
        }
        else{
            URL =  LoadPlaylistFromURL(URL);
            console.log(URL);
        }
    }

}
 function LoadPlaylistFromURL(URL){
    $.ajax({
        url:URL,
        headers:{
            'Authorization': 'Bearer ' + String(Cookies.get("AuthToken")),
        },
        success:function(response){
            console.log("success");
            for(i of response["items"]){
                PushItemToTable(i);
            }
            return response["next"]
        },
        fail:function(response){
            console.log("Failure");
            return null;
        }
    });

}
function LoadUserPlaylists(){
    $.ajax({
        url:"https://api.spotify.com/v1/me/playlists",
        headers:{
            'Authorization': 'Bearer ' + String(Cookies.get("AuthToken")),
        },
        success:function(response){
            console.log
            for(i of response["items"]){
                PushItemToTable(i);
            }
            console.log(response["next"]);
           LoadUserPlaylistURLController(response["next"]);
            for (item of PlaylistChoices){
                PushItemToTable(item);
            }
            console.log(PlaylistChoices);
        }
    });
}

function PushItemToTable(Item){
    console.log("called")
    var StartingUl = document.getElementById("TableOfPlaylists");
    var NewItem = document.createElement("li");
    NewItem.appendChild(document.createTextNode(Item["name"]));
    NewItem.setAttribute("id",Item["id"]);
    StartingUl.appendChild(NewItem);
    $('#'+(Item["id"])).attr('onclick','Playlist(this.id)')

}
function Playlist(item){
    PlaylistSelected  = item;
    $.ajax({
        url:'https://api.spotify.com/v1/playlists/'+item,
        headers:{
            'Authorization': 'Bearer ' + String(Cookies.get("AuthToken")),
        },
        success:function(response){
            console.log(response);
            if(response["snapshot_id"]){
                var CurrentGroup = sessionStorage.getItem("CurrentGroup");//this is questionable
                $.post("/RecordNewPlaylist",{PlaylistId:PlaylistSelected,GroupId:CurrentGroup}).done(function(){
                    console.log("Playlist Sent")
                });
            }
}
    })
}


