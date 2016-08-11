// Modify this file, DO NOT MODIFY main.js, use a JSX to JS Transformer as needed
// Copyright (C) 2015 Peter Steffey

//converts string of seconds into a proper date format
String.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10); // don't forget the second param
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    var time = hours+':'+minutes+':'+seconds;
    return time;
}

function writeToFile(settings) {
    var fso = new ActiveXObject("Scripting.FileSystemObject");
    var settingsFile = fso.OpenTextFile('settings.json', 2, false, 0);
    var fileToRead = fso.OpenTextFile('settings.json', 1, false, 0);
    settingsFile.write(JSON.stringify(settings));
    settingsFile.close();
}



//basically contains everything
var Main = React.createClass({displayName: "Main",
  componentDidMount: function() {
    this.readTextFile();
    this.readSettingsFile();
    window.addEventListener("resize", this.updateDims);
    this.updateFile(); // starts recursize refresh
    this.getIP();
  },
  getIP: function() {
    var parent = this;
    //NOTE: window.RTCPeerConnection is "not a constructor" in FF22/23
    var RTCPeerConnection = /*window.RTCPeerConnection ||*/ window.webkitRTCPeerConnection || window.mozRTCPeerConnection;

    if (RTCPeerConnection) (function () {
        var rtc = new RTCPeerConnection({iceServers:[]});
        if (1 || window.mozRTCPeerConnection) {      // FF [and now Chrome!] needs a channel/stream to proceed
            rtc.createDataChannel('', {reliable:false});
        };

        rtc.onicecandidate = function (evt) {
            // convert the candidate to SDP so we can run it through our general parser
            // see https://twitter.com/lancestout/status/525796175425720320 for details
            if (evt.candidate) grepSDP("a="+evt.candidate.candidate);
        };
        rtc.createOffer(function (offerDesc) {
            grepSDP(offerDesc.sdp);
            console.log(offerDesc.sdp);
            rtc.setLocalDescription(offerDesc);
        }, function (e) { parent.setState({"ip": ""}); });

        var addrs = Object.create(null);
        addrs["0.0.0.0"] = false;
        function updateDisplay(newAddr) {
            if (newAddr in addrs) return;
            else addrs[newAddr] = true;
            var displayAddrs = Object.keys(addrs).filter(function (k) { return addrs[k]; });
            parent.setState({"ip": (displayAddrs.join(", ") || "n/a")});
        }

        function grepSDP(sdp) {
            var hosts = [];
            sdp.split('\r\n').forEach(function (line) { // c.f. http://tools.ietf.org/html/rfc4566#page-39
                if (~line.indexOf("a=candidate")) {     // http://tools.ietf.org/html/rfc4566#section-5.13
                    var parts = line.split(' '),        // http://tools.ietf.org/html/rfc5245#section-15.1
                        addr = parts[4],
                        type = parts[7];
                    if (type === 'host') updateDisplay(addr);
                } else if (~line.indexOf("c=")) {       // http://tools.ietf.org/html/rfc4566#section-5.7
                    var parts = line.split(' '),
                        addr = parts[2];
                    updateDisplay(addr);
                }
            });
        }
    })(); else {
      parent.setState({"ip": ""});
    }
  },
  updateFile: function() {
    var parent = this;
    setInterval(function() {
      parent.readTextFile();
      parent.forceUpdate();
    }, 1000); // 1000 ms = 1 second
  },
  updateDims: function() {
      this.forceUpdate(); // reload page if the user expands the window
  },
  readTextFile: function() {
      var parent = this;

      $.getJSON("score.json", function(json) {
        parent.setState({"vulnerabilities": json});
      });
  },
  readSettingsFile: function() {
    var parent = this;

    $.getJSON("settings.json", function(json) {
      parent.setState({"settings": json});
    });
  },
  getInitialState: function () {
    return {
      "vulnerabilities": [],
      "settings": {},
      "ip":""
    }
  },
  setTeamId: function(button) {
    this.setState({"teamID": button.state.teamID});
  },
  render: function() {

    //styling
    var backDivStyle = {
      position: 'absolute',
      backgroundColor: '#336699',
      left: 0,
      top: 0,
      width: window.innerWidth < 950 ? 950 : window.innerWidth,
      height: window.innerHeight
    };
    var containerDivStyle = {
      position: 'absolute',
      backgroundColor: 'white',
      width: 900,
      left: Math.max((window.innerWidth - 900)/2, 25),
      minWidth: 600,
      top: 10,
      boxShadow: '0px 0px 12px #003366',
      paddingBottom: 10
    };
    var imageStyle = {
      marginTop: 15,
      width: 150,
      height: 150,
      display: 'block',
      marginLeft: 'auto',
      marginRight: 'auto'
    };
    var centerStyle = {
      marginLeft: 0,
      width: '100%',
      textAlign: 'center',
      fontFamily: 'Arial, Verdana, sans-serif'
    };
    var redCenterStyle = {
      marginLeft: 0,
      width: '100%',
      textAlign: 'center',
      fontFamily: 'Arial, Verdana, sans-serif',
      color: 'red'
    };
    var leftStyle = {
      fontFamily: 'Arial, Verdana, sans-serif',
      marginLeft: 10
    };
    var greenStyle = {
      color: 'green'
    };
    var textStyle = {
      marginLeft: 25,
      marginTop: 0,
      marginBottom: 0,
      fontFamily: 'Arial, Verdana, sans-serif'
    };
    var listStyle = {
      fontFamily: 'Arial, Verdana, sans-serif',
      marginLeft: 10,
      listStyleType: 'none'
    };

    //gets file string and splits into array by row
    vulnerabilities = this.state.vulnerabilities;

    settings = this.state.settings;

    var timeLeft = 0;
    var runningTime = 0;
    var limit = settings['limit'];

    if (settings != null && limit != -1) {
      //running time
      var now = new Date(); // current date
      var time = now.toString().split(' ')[4].split(':'); // time componenet in the form 00:00:00
      var now = (parseInt(time[0]) * 3600) + (parseInt(time[1]) * 60) + parseInt(time[2]); // seconds into day
      var past = settings['start']; // gets seconds into day when the scoring engine was started

      runningTime = now - past // difference between the two

      timeLeft = limit - runningTime
    }

    //calculations
    var teamID = 1;

    var numberOfPointsTotal = settings['points'];
    var numberOfPenalties = 0;
    var pointsLost = 0;
    var numberOfComplete = 0;
    var numberTotal = settings['count'];
    var pointsGained = 0;
    var numberOfPointsRecieved = 0;

    var limitStyle = timeLeft < 1800 ? redCenterStyle : centerStyle
    var limitStyle2 = timeLeft > 0 ? centerStyle : redCenterStyle

    var completeList = [];
    var penaltyList = [];
    vulnerabilities.forEach( function(item, i) {
      if (item['mode'] == true) {
        if (item['complete'] == true) {                               // if analyze.py has marked this item as complete
          numberOfComplete++;                                         // iterate number of complete items
          pointsGained += item['points'];                             // append to number of points gained
          completeList.push(React.createElement(ListItem, {item: item, key: i}))         // returns the custum html element for this item
        }
      }
      else {
        if (item['complete'] == true) {
          numberOfPenalties++;                                      // if analyze.py has marked this item as complete
          pointsLost += item['points'];                             // append to number of points gained
          penaltyList.push(React.createElement(ListItem, {item: item, key: i}))        // returns the custum html element for this item
        }
      }
    });

    //keeps background blue for full height
    if (window.innerHeight < (750 + (20 * (numberTotal+numberOfPenalties)))) {
      backDivStyle.height = 750 + (20 * (numberTotal+numberOfPenalties));
    }

    var id = (settings['id'] == '' ? React.createElement("h3", {style: redCenterStyle}, "Team ID: Please run the 'Set ID' program on the desktop") : React.createElement("h3", {style: centerStyle}, "Team ID: ", settings['id']));

    numberOfPointsRecieved = pointsGained - pointsLost;

    var runningTimeLabel = '';
    var timeLeftLabel = '';

    if (limit != -1) {
      runningTimeLabel = runningTime.toString().toHHMMSS();
      timeLeftLabel = (timeLeft > 0 ? timeLeft.toString().toHHMMSS() : "Out of Time!");
      if (runningTime < 0) {
        limitStyle2 = redCenterStyle;
        runningTimeLabel = "Error: The time now is earlier than when the image was started"
        timeLeftLabel = "Error"
      }
    }

    var ipStr = this.state.ip;
    var ip = null;
    if (ipStr != '') {
      ip = React.createElement("h3", {style: centerStyle}, "Image IP Address: ", ipStr);
    }

    return (
      React.createElement("div", {style: backDivStyle}, 
        React.createElement("div", {style: containerDivStyle}, 
          React.createElement("img", {src: "icon.png", style: imageStyle}), 
          React.createElement("h1", {style: centerStyle}, "LWASP Cyber Security Training Image: ", settings['name']), 
          React.createElement("h2", {style: centerStyle}, "Report Generated at ", Date()), 
          limit == -1 ? null : React.createElement("h3", {style: limitStyle2}, "Image Running Time: ", runningTimeLabel), 
          limit == -1 ? null : React.createElement("h3", {style: limitStyle}, "Image Time Remaining: ", timeLeftLabel), 
          id, 
          ip, 
          React.createElement("h2", {style: centerStyle}, numberOfPointsRecieved, " out of ", numberOfPointsTotal, " points received"), 
          React.createElement("br", null), 
          React.createElement("h3", {style: leftStyle}, numberOfPenalties, " penalties assessed, for a loss of ", pointsLost, " points:"), 
          React.createElement("li", {style: listStyle}, penaltyList), 
          React.createElement("h3", {style: leftStyle}, numberOfComplete, " out of ", numberTotal, " scored security issues fixed, for a gain of ", pointsGained, " points:"), 
          React.createElement("li", {style: listStyle}, completeList), 
          completeList.length == 0 ? React.createElement("h3", {style: leftStyle}, "Get out there and score some points!") : null
        )
      )
    );
  }
});

var SetButton = React.createClass({displayName: "SetButton",
  mixins: [React.addons.LinkedStateMixin],
  set: function () {
    this.setState({"editing": true, "teamID": ""});
  },
  done: function() {
    this.setState({"editing": false, "label": 'Change'});
    var settings = this.props.settings;
    settings['name'] = this.state.teamID;
    writeToFile(settings)
    document.cookie = "id="+this.state.teamID+"; expires=Thu, 31 Dec 2015 12:00:00 UTC";
    console.log('Logging ' + this.state.teamID);
  },
  getInitialState: function () {
    return {
      "editing": false,
      "teamID": 'Not Set',
      "label": 'Set'
    }
  },
  render: function() {

    var buttonStyle = {
      marginLeft: 10,
      marginTop: -10,
      float: 'top'
    };
    var internal = (this.state.editing ? React.createElement("div", {style: this.props.style}, React.createElement("input", {valueLink: this.linkState('teamID')}), React.createElement("button", {style: buttonStyle, onClick: this.done}, "Done")) : React.createElement("div", null, React.createElement("h3", {style: this.props.style}, "Team ID: ", this.state.teamID, React.createElement("button", {style: buttonStyle, onClick: this.set}, this.state.label))));
    return internal;
  }
});

var ListItem = React.createClass({displayName: "ListItem",
  render: function () {
    var style = {
      paddingLeft: 15
    };
    return React.createElement("li", {key: this.props.key, style: style}, this.props.item['title'], " - ", this.props.item['points'], " pts")
  }
});

React.render(React.createElement(Main, null), document.getElementById('mountingpoint'));