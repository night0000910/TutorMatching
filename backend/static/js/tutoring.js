// グローバル変数・状態の管理
let webSocket = null;
let localStream = new MediaStream();
let mapPeers = {};
let currentUsername = "";

const rtcConfiguration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
    ]
};

$(document).ready(function() {
    const request = new XMLHttpRequest();
    request.open("GET", "/api/v1/users/authenticated_user/classes/current_class/");
    request.onload = communicateWithWebRTC;
    request.send();
});

async function communicateWithWebRTC() {
    const response = JSON.parse(this.response);
    const currentClass = response[0];

    if (!currentClass) return;

    const usernameElement = document.getElementById("username");
    currentUsername = usernameElement ? usernameElement.value : "";

    const userIdElement = document.getElementById("user-id");
    const userId = userIdElement ? userIdElement.value : "";
    const classId = currentClass.id;

    // 1. まずカメラ・マイクのストリームを取得する (必須)
    const constraints = { video: true, audio: true };
    const localVideo = document.querySelector("#local-video");
    const btnToggleVideo = document.querySelector("#btn-toggle-video");
    const btnToggleAudio = document.querySelector("#btn-toggle-audio");

    try {
        localStream = await navigator.mediaDevices.getUserMedia(constraints);
        if (localVideo) {
            localVideo.srcObject = localStream;
            localVideo.muted = true;
        }

        const videoTracks = localStream.getVideoTracks();
        const audioTracks = localStream.getAudioTracks();

        if (btnToggleVideo && videoTracks.length > 0) {
            btnToggleVideo.addEventListener("click", () => {
                videoTracks[0].enabled = !videoTracks[0].enabled;
                btnToggleVideo.innerHTML = videoTracks[0].enabled
                    ? '<i class="material-icons right">camera_alt</i>カメラをオフ'
                    : '<i class="material-icons right">camera_alt</i>カメラをオン';
            });
        }

        if (btnToggleAudio && audioTracks.length > 0) {
            btnToggleAudio.addEventListener("click", () => {
                audioTracks[0].enabled = !audioTracks[0].enabled;
                btnToggleAudio.innerHTML = audioTracks[0].enabled
                    ? '<i class="material-icons right">blur_on</i>ミュート'
                    : '<i class="material-icons right">blur_on</i>ミュート解除';
            });
        }
    } catch (error) {
        console.error("メディアデバイスへのアクセスに失敗しました", error);
        return;
    }

    // メッセージ送信ボタンのイベント
    const btnSendMsg = document.querySelector("#btn-send-msg");
    if (btnSendMsg) {
        btnSendMsg.addEventListener("click", sendMsgOnClick);
    }

    // 2. カメラの準備が完了してから WebSocket 接続を開始する
    const loc = window.location;
    const wsStart = loc.protocol === "https:" ? "wss://" : "ws://";
    const endPoint = `${wsStart}${loc.host}/signaling/${classId}/${userId}/`;

    console.log("WebSocket接続先 : ", endPoint);
    webSocket = new WebSocket(endPoint);

    webSocket.addEventListener("open", () => {
        console.log("WebSocketでの接続に成功しました");
        // 接続成功を部屋メンバーに通知
        sendSignal("new-peer", {});
    });

    webSocket.addEventListener("message", webSocketOnMessage);
    webSocket.addEventListener("close", () => console.log("WebSocketが切断されました"));
    webSocket.addEventListener("error", (e) => console.error("WebSocketエラー", e));
}

function webSocketOnMessage(event) {
    const parsedData = JSON.parse(event.data);
    const peerUsername = parsedData["peer"];
    const action = parsedData["action"];

    // 自分の送信メッセージはスキップ
    if (currentUsername === peerUsername) return;

    const receiver_channel_name = parsedData["message"] ? parsedData["message"]["receiver_channel_name"] : null;

    if (action === "new-peer") {
        createOfferer(peerUsername, receiver_channel_name);
        return;
    }

    if (action === "new-offer") {
        const offer = parsedData["message"]["sdp"];
        createAnswerer(offer, peerUsername, receiver_channel_name);
        return;
    }

    if (action === "new-answer") {
        const answer = parsedData["message"]["sdp"];
        const peerObj = mapPeers[peerUsername];
        if (peerObj) {
            peerObj[0].setRemoteDescription(new RTCSessionDescription(answer));
        }
        return;
    }

    if (action === "candidate") {
        const candidate = parsedData["message"]["candidate"];
        const peerObj = mapPeers[peerUsername];
        if (peerObj && candidate) {
            peerObj[0].addIceCandidate(new RTCIceCandidate(candidate));
        }
        return;
    }

    // 相手が退室した場合の処理
    if (action === "user-left") {
        if (mapPeers[peerUsername]) {
            const peer = mapPeers[peerUsername][0];
            peer.close();
            delete mapPeers[peerUsername];
            const remoteVideo = document.getElementById(`${peerUsername}-video`);
            if (remoteVideo) removeVideo(remoteVideo);
        }
    }
}

function sendSignal(action, message) {
    if (!webSocket || webSocket.readyState !== WebSocket.OPEN) return;
    const jsonStr = JSON.stringify({
        "peer": currentUsername,
        "action": action,
        "message": message
    });
    webSocket.send(jsonStr);
}

function createOfferer(peerUsername, receiver_channel_name) {
    const peer = new RTCPeerConnection(rtcConfiguration);
    addLocalTracks(peer);

    const dc = peer.createDataChannel("channel");
    dc.addEventListener("open", () => console.log("DataChannel接続完了"));
    dc.addEventListener("message", dcOnMessage);

    const remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    mapPeers[peerUsername] = [peer, dc];

    // ICE Candidate の個別送信
    peer.addEventListener("icecandidate", (event) => {
        if (event.candidate) {
            sendSignal("candidate", {
                "candidate": event.candidate,
                "receiver_channel_name": receiver_channel_name
            });
        }
    });

    peer.addEventListener("iceconnectionstatechange", () => {
        const state = peer.iceConnectionState;
        if (state === "failed" || state === "disconnected" || state === "closed") {
            delete mapPeers[peerUsername];
            if (state !== "closed") peer.close();
            removeVideo(remoteVideo);
        }
    });

    // SDP Offer の生成と送信
    peer.createOffer()
        .then(offer => peer.setLocalDescription(offer))
        .then(() => {
            console.log("Offerを送信します");
            sendSignal("new-offer", {
                "sdp": peer.localDescription,
                "receiver_channel_name": receiver_channel_name
            });
        })
        .catch(e => console.error("Offer作成エラー:", e));
}

function createAnswerer(offer, peerUsername, receiver_channel_name) {
    const peer = new RTCPeerConnection(rtcConfiguration);
    addLocalTracks(peer);

    const remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    peer.addEventListener("datachannel", e => {
        peer.dc = e.channel;
        peer.dc.addEventListener("open", () => console.log("DataChannel(Answer側)接続完了"));
        peer.dc.addEventListener("message", dcOnMessage);
        mapPeers[peerUsername] = [peer, peer.dc];
    });

    // ICE Candidate の個別送信
    peer.addEventListener("icecandidate", (event) => {
        if (event.candidate) {
            sendSignal("candidate", {
                "candidate": event.candidate,
                "receiver_channel_name": receiver_channel_name
            });
        }
    });

    peer.addEventListener("iceconnectionstatechange", () => {
        const state = peer.iceConnectionState;
        if (state === "failed" || state === "disconnected" || state === "closed") {
            delete mapPeers[peerUsername];
            if (state !== "closed") peer.close();
            removeVideo(remoteVideo);
        }
    });

    // Remote Description セット後に Answer を作成・送信
    peer.setRemoteDescription(new RTCSessionDescription(offer))
        .then(() => peer.createAnswer())
        .then(answer => peer.setLocalDescription(answer))
        .then(() => {
            console.log("Answerを送信します");
            sendSignal("new-answer", {
                "sdp": peer.localDescription,
                "receiver_channel_name": receiver_channel_name
            });
        })
        .catch(e => console.error("Answer作成エラー:", e));
}

function addLocalTracks(peer) {
    localStream.getTracks().forEach(track => {
        peer.addTrack(track, localStream);
    });
}

function setOnTrack(peer, remoteVideo) {
    const remoteStream = new MediaStream();
    remoteVideo.srcObject = remoteStream;

    peer.addEventListener("track", (event) => {
        remoteStream.addTrack(event.track);
    });
}

function sendMsgOnClick() {
    const firstNameElem = document.getElementById("first-name");
    const lastNameElem = document.getElementById("last-name");
    const firstName = firstNameElem ? firstNameElem.getAttribute("value") : "";
    const lastName = lastNameElem ? lastNameElem.getAttribute("value") : "";
    
    const messageInput = document.querySelector("#msg");
    const messageList = document.querySelector("#message-list");
    if (!messageInput || !messageList) return;

    const message = messageInput.value;
    if (!message.trim()) return;

    const fullMsg = `${lastName} ${firstName} : ${message}`;

    const li = document.createElement("li");
    li.style.listStyleType = "none";
    li.appendChild(document.createTextNode(fullMsg));
    messageList.appendChild(li);

    const dataChannels = getDataChannels();
    dataChannels.forEach(dc => {
        if (dc && dc.readyState === "open") {
            dc.send(fullMsg);
        }
    });

    messageInput.value = "";
}

function dcOnMessage(event) {
    const messageList = document.querySelector("#message-list");
    if (!messageList) return;
    const li = document.createElement("li");
    li.style.listStyleType = "none";
    li.appendChild(document.createTextNode(event.data));
    messageList.appendChild(li);
}

function createVideo(peerUsername) {
    const videoContainer = document.querySelector("#video-container");
    const remoteVideo = document.createElement("video");

    remoteVideo.id = `${peerUsername}-video`;
    remoteVideo.autoplay = true;
    remoteVideo.playsInline = true;

    const videoWrapper = document.createElement("div");
    videoWrapper.setAttribute("class", "section");

    if (videoContainer) {
        videoContainer.appendChild(videoWrapper);
        videoWrapper.appendChild(remoteVideo);
    }

    return remoteVideo;
}

function removeVideo(video) {
    const videoWrapper = video.parentNode;
    if (videoWrapper && videoWrapper.parentNode) {
        videoWrapper.parentNode.removeChild(videoWrapper);
    }
}

function getDataChannels() {
    const dataChannels = [];
    for (let peerUsername in mapPeers) {
        if (mapPeers[peerUsername][1]) {
            dataChannels.push(mapPeers[peerUsername][1]);
        }
    }
    return dataChannels;
}