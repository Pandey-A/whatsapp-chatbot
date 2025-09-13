# New: Generate interactive message with reply buttons
def get_interactive_reply_button_input(recipient, body_text, button1_id, button1_title, button2_id, button2_title):
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": button1_id, "title": button1_title}},
                    {"type": "reply", "reply": {"id": button2_id, "title": button2_title}}
                ]
            }
        }
    })
import logging
from flask import current_app, jsonify
import json
import requests

# from app.services.openai_service import generate_response
import re


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


# New: Generate document message input
def get_document_message_input(recipient, media_id=None, media_url=None, caption=None, filename=None):
    document = {}
    if media_id:
        document["id"] = media_id
    if media_url:
        document["link"] = media_url
    if caption:
        document["caption"] = caption
    if filename:
        document["filename"] = filename
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "document",
        "document": document
    })


def generate_response(response):
    # Return text in uppercase
    return response.upper()


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    logging.info(f"Incoming WhatsApp message: {json.dumps(message)}")


    # Handle WhatsApp interactive button reply
    if message.get("type") == "interactive":
        interactive = message.get("interactive", {})
        if interactive.get("type") == "button_reply":
            button_reply_id = interactive["button_reply"].get("id")
            if button_reply_id == "iternary_btn":
                media_id = "676557238187990"  # Your actual media ID
                caption = "Here is your itinerary."
                filename = "itinerary.pdf"
                data = get_document_message_input(
                    wa_id,
                    media_id=media_id,
                    caption=caption,
                    filename=filename
                )
                send_message(data)
                return
            elif button_reply_id == "more_btn":
                response = "You selected More. Please specify what you need."
                data = get_text_message_input(wa_id, response)
                send_message(data)
                return

    # If user sends any text, show interactive buttons
    if message.get("type") == "text":
        message_body = message["text"]["body"]
        # Show buttons for any text message
        data = get_interactive_reply_button_input(
            wa_id,
            body_text="Choose an option:",
            button1_id="iternary_btn",
            button1_title="Iternary",
            button2_id="more_btn",
            button2_title="More"
        )
        send_message(data)
        return


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
