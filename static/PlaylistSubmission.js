var PlaylistChoices = [];

function PlaylistBoxLoad(){
    document.getElementById("SubmissionOverlay").style.display = "block";
    LoadUserPlaylists();
}

function LoadUserPlaylists(){
    $.ajax({
        url:"https://api.spotify.com/v1/me/playlists",
        headers:{
            'Authorization': 'Bearer ' + String(Cookies.get("AuthToken")),
        },
        success:function(response){
            for(i of response["items"]){
                PlaylistChoices.push(i);
            }
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
            if(response["description"]){
                var CurrentGroup = sessionStorage.getItem("CurrentGroup");//this is questionable
                $.post("/RecordNewPlaylist",{PlaylistId:PlaylistSelected,GroupId:CurrentGroup}).done(function(){
                    console.log("Playlist Sent")
                });
            }
}


