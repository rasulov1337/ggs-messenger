"use strict"


const CHAT_API_URL = 'http://localhost:8000/chats/'

async function init() {
    const response = await fetch(CHAT_API_URL + 'get-cent-token')

    if (!response.ok) {
        throw new Error(response.message)
    }
    const centrifugoData = await response.json()

    const centrifuge = new Centrifuge(centrifugoData.url, {
        token: centrifugoData.token
    });


    centrifuge.on('connecting', function (ctx) {
        console.log(`connecting: ${ctx.code}, ${ctx.reason}`);
    }).on('connected', function (ctx) {
        console.log(`connected over ${ctx.transport}`);
    }).on('disconnected', function (ctx) {
        console.log(`disconnected: ${ctx.code}, ${ctx.reason}`);
    }).connect();

    const sub = centrifuge.newSubscription('channel');

    sub.on('publication', onMessageReceive).subscribe();
}


function sendMessage(chatId, text) {
    const requst = new Request(CHAT_API_URL + `${chatId}/messages/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: text,
        })
    })

    fetch(requst)
}


function editMessage(chatId, messageId, text) {
    const requst = new Request(CHAT_API_URL + `${chatId}/messages/${messageId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            chatId: chatId,
            messageId: messageId,
            text: text,
        })
    })

    fetch(requst)
}

function deleteMessage(chatId, messageId) {
    const requst = new Request(CHAT_API_URL + `${chatId}/messages/${messageId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            chatId: chatId,
            messageId: messageId,
        })
    })

    fetch(requst)
}

function onMessageReceive(ctx) {
    // По идее копию HTML элемента создаем, но так как фронэнда нет, то ждем-с
    console.log(ctx.data)
}



init()
