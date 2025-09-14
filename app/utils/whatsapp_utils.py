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


def send_tour_options(wa_id):
    """Send interactive buttons with tour options"""
    # Create the button payload with 3 buttons
    button_payload = {
        "messaging_product": "whatsapp",
        "to": wa_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "Choose your experience:"},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "yuva_yatra_1_btn",
                            "title": "1️⃣ Yuva Yatra 1"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "yuva_yatra_2_btn", 
                            "title": "2️⃣ Yuva Yatra 2"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "parivar_pravaas_btn",
                            "title": "3️⃣ Parivaar Pravas"
                        }
                    }
                ]
            }
        }
    }
    send_message(json.dumps(button_payload))


def send_cta_message(wa_id):
    """Send CTA message with call buttons"""
    cta_msg = json.dumps({
        "messaging_product": "whatsapp",
        "to": wa_id,
        "type": "interactive",
        "interactive": {
            "type": "cta_url",
            "body": {"text": "For Any Queries- Call at 8800969741, To Confirm and Make the payment- Call at 7054400500"},
            "action": {
                "name": "cta_url",
                "parameters": [
                    {"display_text": "Call for Queries", "url": "tel:8800969741"},
                    {"display_text": "Call for Payment", "url": "tel:7054400500"}
                ]
            }
        }
    })
    send_message(cta_msg)


def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_type = message.get("type")

    # Handle interactive button replies
    if message_type == "interactive":
        interactive = message.get("interactive", {})
        if interactive.get("type") == "button_reply":
            button_reply_id = interactive["button_reply"].get("id")
            
            if button_reply_id == "yuva_yatra_1_btn":
                # Send Yuva Yatra 1 PDF
                data = json.dumps({
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": wa_id,
                    "type": "document",
                    "document": {
                        "id": "1311569197013460",
                        "caption": "Yuva Yatra 1 PDF - Separate dorms & unattached washrooms for men and women 🛏️🚻",
                        "filename": "yuva_yatra_1.pdf"
                    }
                })
                send_message(data)
                send_cta_message(wa_id)
                return
                
            elif button_reply_id == "yuva_yatra_2_btn":
                # Send Yuva Yatra 2 PDF
                data = json.dumps({
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": wa_id,
                    "type": "document",
                    "document": {
                        "id": "683872947367766",
                        "caption": "Yuva Yatra 2 PDF - Mixed & female dorms with attached washrooms 🏠",
                        "filename": "yuva_yatra_2.pdf"
                    }
                })
                send_message(data)
                send_cta_message(wa_id)
                return
                
            elif button_reply_id == "parivar_pravaas_btn":
                # Send Parivaar Pravas PDF
                data = json.dumps({
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": wa_id,
                    "type": "document",
                    "document": {
                        "id": "1813897679248489",
                        "caption": "Parivaar Pravas PDF - Comfortable family stay options 👨‍👩‍👧‍👦",
                        "filename": "parivar_pravaas.pdf"
                    }
                })
                send_message(data)
                send_cta_message(wa_id)
                return
                
            elif button_reply_id == "customized_tour_btn":
                # Send custom message for Customized Tour
                custom_msg = (
                    "Thank you for your interest in a customized tour! 🌟\n\n"
                    "Our team will help you create a personalized Dev Deepawali experience in Varanasi.\n\n"
                    "Please call us to discuss your requirements:"
                )
                send_message(get_text_message_input(wa_id, custom_msg))
                send_cta_message(wa_id)
                return

    # Handle text messages (including "Hi", "Hello", etc.)
    elif message_type == "text":
        # Always send the welcome message first
        welcome_text = (
            f"Namaste {name}! 🙏\n\n"
            "Welcome to HostmenIndia! ✨\n\n"
            "Experience the spiritual grandeur of Dev Deepawali in Varanasi – from Delhi to Delhi or from your own city.\n\n"
            "Choose from our curated tours and get your complete itinerary instantly:"
        )
        welcome_msg = get_text_message_input(wa_id, welcome_text)
        send_message(welcome_msg)
        
        # Send tour options immediately after welcome message
        send_tour_options(wa_id)
        return

    # Handle other message types (audio, image, etc.)
    else:
        fallback_msg = (
            f"Hello {name}! 👋\n\n"
            "I can help you with information about our Dev Deepawali tours in Varanasi.\n\n"
            "Please choose from the options below:"
        )
        send_message(get_text_message_input(wa_id, fallback_msg))
        send_tour_options(wa_id)


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