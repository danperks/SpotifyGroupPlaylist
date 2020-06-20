function Logout() {

    document.cookie = "UserId=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "RefreshToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "AuthToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.replace("/");
}

function LeaveGroup() {
    sessionStorage.setItem("CurrentGroup", "");
    sessionStorage.setItem("CurrentName", "");
    location.reload();
}

function DeleteGroup() {
    GroupToLeave = document.getElementById("EnteredGroup").value;
    $.get("/Management/AbandonGroup", { GroupCode: GroupToLeave }).done(function() { RefreshGroups() });
    sessionStorage.setItem("CurrentGroup", "");
    sessionStorage.setItem("CurrentName", "");
    location.reload();

}

function Submission() {
    code = document.getElementById("EnteredGroup").value;
    sessionStorage.setItem("CurrentGroup", code);
    $.ajax("/api/UserGroups").done(function(data) {
        console.log(data)
        ind = data[0].indexOf(code)
        if (data.length > 1) {
            sessionStorage.setItem("CurrentName", data[1][ind]);
        } else {
            sessionStorage.setItem("CurrentName", "New Group");
        }
        document.getElementById("joinform").submit();
    });
}


function RefreshGroups() {
    $('#GroupTable').empty();
    $.ajax("/api/UserGroups").done(function(data) {
        var table = document.getElementById("GroupTable");
        var header = table.insertRow();
        header.insertCell(0).innerHTML = "Group Name".bold();
        header.insertCell(1).innerHTML = "Group Code".bold();
        if (data.length > 1) {
            for (i = 0; i < data[0].length; i++) {
                var row = table.insertRow();
                row.insertCell(0).innerHTML = data[1][i];
                row.insertCell(1).innerHTML = data[0][i];
            }
        } else {
            table.style.display = "None";
            document.getElementById("groups").innerHTML = "No Groups Found";
        }
    });
    return "Table Updated";
}

$(document).ready(
    RefreshGroups());

function CreateAGroup() {
    DeafultUserName = String(Cookies.get("UserId")) + "'s Group";
    GroupNameEntry = window.prompt("Enter A Group Name", DeafultUserName);
    if (GroupNameEntry) {
        $.post("/CreateGroup", { GroupName: GroupNameEntry }).done(function(data) {
            alert("Your Playlist Code is: " + String(data));
            sessionStorage.setItem("CurrentGroup", String(data))
            sessionStorage.setItem("CurrentName", GroupNameEntry)
            location.reload()
        });
    }
}

function onLoad() {
    cur = sessionStorage.getItem("CurrentGroup");
    CurrentName = sessionStorage.getItem("CurrentName");
    if (cur == "" || cur == null) {
        document.getElementById("votebut").style.display = "none";
        document.getElementById("leavebut").style.display = "none";
        document.getElementById("delbut").style.display = "none";
        document.getElementById("status").innerHTML = "Not In Group";
    } else if (cur != "") {
        document.getElementById("joinbut").style.display = "none";
        document.getElementById("createbut").style.display = "none";
        document.getElementById("status").innerHTML = "Currently Editing " + CurrentName;
        codein = document.getElementById("EnteredGroup");
        codein.disabled = true;
        codein.value = cur;
    }

}

onLoad()