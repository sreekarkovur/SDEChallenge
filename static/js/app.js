// Configure Pusher instance
const pusher = new Pusher('0011ebc3764957afb33d', {
  cluster: 'ap2',
  encrypted: true
});

var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    $(document).ready(function(){
        var dataTable = $("#dataTable").DataTable()
        // var userSessions = $("#userSessions").DataTable()
        var pages = $("#pages").DataTable()

        axios.get('/get-all-sessions')
        .then(response => {
              response.data.forEach((data) => {
                  insertDatatable(data)
              })
          var d = new Date();
          var updatedAt = `${d.getFullYear()}/${months[d.getMonth()]}/${d.getDay()} ${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}`
          document.getElementById('session-update-time').innerText = updatedAt
        })

        var sessionChannel = pusher.subscribe('session');
        sessionChannel.bind('new', function(data) {
            insertDatatable(data)
        });

        var d = new Date();
        var updatedAt = `${d.getFullYear()}/${months[d.getMonth()]}/${d.getDay()} ${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}`
        document.getElementById('session-update-time').innerText = updatedAt
    });

    function insertDatatable(data){
        var dataTable = $("#dataTable").DataTable()
        dataTable.row.add([
            data.time,
            data.ip,
            data.continent,
            data.country,
            data.city,
            data.os,
            data.browser,
            `<a href=${"/dashboard/"+data.session}>View pages visited</a>`
          ]);
          dataTable.order([0, 'desc']).draw();
    }