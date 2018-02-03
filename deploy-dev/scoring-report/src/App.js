import React, { Component } from 'react';
import './App.css';
import $ from 'jquery';
import Icon from './icon.png';

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

//basically contains everything
class Main extends Component {
  state = {
    "vulnerabilities": [],
    "settings": {},
    "ip":""
  }

  componentDidMount() {
    this.readTextFile();
    this.readSettingsFile();
    window.addEventListener("resize", this.updateDims.bind(this));
    this.updateFile(); // starts recursize refresh
    this.getIP();
  }

  getIP() {
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
            sdp.split('\r\n').forEach(function (line) { // c.f. http://tools.ietf.org/html/rfc4566#page-39
                if (~line.indexOf("a=candidate")) {     // http://tools.ietf.org/html/rfc4566#section-5.13
                    let parts = line.split(' '),        // http://tools.ietf.org/html/rfc5245#section-15.1
                        addr = parts[4],
                        type = parts[7];
                    if (type === 'host') updateDisplay(addr);
                } else if (~line.indexOf("c=")) {       // http://tools.ietf.org/html/rfc4566#section-5.7
                    let parts = line.split(' '),
                        addr = parts[2];
                    updateDisplay(addr);
                }
            });
        }
    })(); else {
      parent.setState({"ip": ""});
    }
  }

  updateFile() {
    var parent = this;
    setInterval(function() {
      parent.readTextFile();
      parent.forceUpdate();
    }, 5000); // 1000 ms = 1 second
  }

  updateDims() {
      this.forceUpdate(); // reload page if the user expands the window
  }

  readTextFile() {
      var parent = this;

      $.getJSON("score.json", function(json) {
        parent.setState({"vulnerabilities": json.score});
      });
  }

  readSettingsFile() {
    var parent = this;

    $.getJSON("settings.json", function(json) {
      parent.setState({"settings": json});
    });
  }

  setTeamId(button) {
    this.setState({"teamID": button.state.teamID});
  }

  render() {
    //gets file string and splits into array by row
    let { vulnerabilities, settings } = this.state;

    let timeLeft = 0;
    let runningTime = 0;
    let limit = settings['limit'];

    if (settings !== null && limit !== -1) {
      //running time
      let now = new Date(); // current date
      let time = now.toString().split(' ')[4].split(':'); // time componenet in the form 00:00:00
      now = (parseInt(time[0]) * 3600) + (parseInt(time[1]) * 60) + parseInt(time[2]); // seconds into day
      let past = settings['start']; // gets seconds into day when the scoring engine was started

      runningTime = now - past // difference between the two

      timeLeft = limit - runningTime
    }

    var numberOfPointsTotal = settings['points'];
    var numberOfPenalties = 0;
    var pointsLost = 0;
    var numberOfComplete = 0;
    var numberTotal = settings['count'];
    var pointsGained = 0;
    var numberOfPointsRecieved = 0;

    var limitClass = timeLeft < 1800 ? 'redCenter' : 'center';
    var limitClass2 = timeLeft > 0 ? 'center' : 'redCenter';

    var completeList = [];
    var penaltyList = [];
    vulnerabilities.forEach( function(item, i) {
      if (item['mode'] == true) {
        numberOfComplete++;                                         // iterate number of complete items
        pointsGained += item['points'];                             // append to number of points gained
        completeList.push(<ListItem item={item} key={i} />)         // returns the custum html element for this item
      }
      else {
        numberOfPenalties++;                                      // if analyze.py has marked this item as complete
        pointsLost += item['points'];                             // append to number of points gained
        penaltyList.push(<ListItem item={item} key={i} />)        // returns the custum html element for this item
      }
    });

    var id = (settings['id'] == '' ? <h3 className="redCenter">Team ID: Please run the 'Set ID' program on the desktop</h3> : <h3 className="center">Team ID: {settings['id']}</h3>);

    numberOfPointsRecieved = pointsGained - pointsLost;

    var runningTimeLabel = '';
    var timeLeftLabel = '';

    if (limit != -1) {
      runningTimeLabel = runningTime.toString().toHHMMSS();
      timeLeftLabel = (timeLeft > 0 ? timeLeft.toString().toHHMMSS() : "Out of Time!");
      if (runningTime < 0) {
        limitClass2 = 'redCenterStyle';
        runningTimeLabel = "Error: The time now is earlier than when the image was started"
        timeLeftLabel = "Error"
      }
    }

    var ipStr = this.state.ip;
    var ip = null;
    if (ipStr != '') {
      ip = <h3 className="center">Image IP Address: {ipStr}</h3>;
    }

    return (
      <div className="backDiv">
        <center>
        <div className="containerDiv">
          <img alt="icon" src={Icon} />
          <h1 className="center">LWASP Cyber Security Training Image: {settings['name']}</h1>
          <h2 className="center">Report Generated at {Date()}</h2>
          {limit == -1 ? null : <h3 className={limitClass2}>Image Running Time: {runningTimeLabel}</h3>}
          {limit == -1 ? null : <h3 className={limitClass}>Image Time Remaining: {timeLeftLabel}</h3>}
          {id}
          {ip}
          <h2 className="center">{numberOfPointsRecieved} out of {numberOfPointsTotal} points received</h2>
          <br></br>
          <h3 className="left">{numberOfPenalties} penalties assessed, for a loss of {pointsLost} points:</h3>
          <li className="list">{penaltyList}</li>
          <h3 className="left">{numberOfComplete} out of {numberTotal} scored security issues fixed, for a gain of {pointsGained} points:</h3>
          <li className="list">{completeList}</li>
          {completeList.length == 0 ? <h3 className="left">Get out there and score some points!</h3> : null}
        </div>
        </center>
      </div>
    );
  }
}

class ListItem extends Component {
  render() {
    var style = {
      paddingLeft: 15
    };
    return <li key={this.props.key} style={style}>{this.props.item['title']} - {this.props.item['points']} pts</li>
  }
}

export default Main;
