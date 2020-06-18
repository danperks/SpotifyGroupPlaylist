function Logout() {

    document.cookie = "UserId=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "RefreshToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "AuthToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.replace("/");
}

function LeaveGroup() {
    GroupToLeave = document.getElementById("EnteredGroup").value;
    $.get("/Management/AbandonGroup", { GroupCode: GroupToLeave }).done(function() { RefreshGroups() });

}

function Submission() {
    sessionStorage.setItem("CurrentGroup", document.getElementById("EnteredGroup").value); //set current group
}

function RefreshGroups() {
    $('#GroupTable').empty();
    $.ajax("/api/UserGroups").done(function(data) {
        var table = document.getElementById("GroupTable")
        var header = table.insertRow();
        var h1 = header.insertCell(0).innerHTML = "Group Name".bold();
        var h2 = header.insertCell(1).innerHTML = "Group Code".bold();
        console.log(data);
        for (i = 0; i < data[0].length; i++) {

            var row = table.insertRow();
            var cell1 = row.insertCell(0).innerHTML = data[1][i];
            var cell2 = row.insertCell(1).innerHTML = data[0][i];

        }
    })

    return "Table Updated"
}
$(document).ready(RefreshGroups());

function CreateAGroup() {
    DeafultUserName = String(Cookies.get("UserId")) + "'s Group";
    GroupNameEntry = window.prompt("Enter A Group Name", DeafultUserName);
    if (GroupNameEntry) {
        $.post("/CreateGroup", { GroupName: GroupNameEntry }).done(function(data) {
            alert("Your New Group is " + String(data));
        });
    }
}