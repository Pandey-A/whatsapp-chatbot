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
    """Send the tour option buttons"""
    # First message with 3 buttons (Options 1, 2, 3)
    button_msg_1 = json.dumps({
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
                            "title": "1️⃣ Yuva Yatra 1 "
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "yuva_yatra_2_btn",
                            "title": "2️⃣ Yuva Yatra 1  "
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "parivar_pravaas_btn",
                            "title": "3️⃣ Parivaar Pravaas"
                        }
                    }
                ]
            }
        }
    })
    send_message(button_msg_1)
    
    # Second message with 1 button (Option 4)
    button_msg_2 = json.dumps({
        "messaging_product": "whatsapp",
        "to": wa_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "Or choose a customized option:"},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "customized_tour_btn",
                            "title": "4️⃣ Customized Tour"
                        }
                    }
                ]
            }
        }
    })
    send_message(button_msg_2)


def is_greeting_message(message_text):
    """Check if the message is a greeting that should trigger welcome flow"""
    greeting_keywords = [
        'hi', 'hello', 'hey', 'start', 'begin', 'namaste', 'namaskar',
        'good morning', 'good afternoon', 'good evening', 'greetings'
    ]
    
    # Convert to lowercase and check if it matches any greeting
    message_lower = message_text.lower().strip()
    
    # Check for exact matches or if message contains greeting words
    return any(keyword in message_lower for keyword in greeting_keywords)


def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_type = message.get("type")

    # Handle interactive button replies FIRST
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
                        "caption": "🏕️ Yuva Yatra 1 – Stay carefree with separate men’s and women’s dorms plus private unattached washrooms for complete comfort, hygiene, and peace of mind.",
                        "filename": "yuva_yatra_1.pdf"
                    }
                })
                send_message(data)
                
                # Send contact message
                contact_msg = (
                    "📞 *Contact Us:*\n\n"
                    "For Any Queries: *8800969741*\n"
                    "To Confirm and Make Payment: *7054400500*\n\n"
                    "Our team is ready to assist you! 😊"
                )
                send_message(get_text_message_input(wa_id, contact_msg))
                
            elif button_reply_id == "yuva_yatra_2_btn":
                # Send Yuva Yatra 2 PDF
                data = json.dumps({
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": wa_id,
                    "type": "document",
                    "document": {
                        "id": "683872947367766",
                        "caption": "🏕️ Yuva Yatra 2 – Stay easy in mixed 👫 and female 👩 dorms, designed with attached washrooms 🚿 for convenience, comfort, and a relaxed journey ✨🛏️.",
                        "filename": "yuva_yatra_2.pdf"
                    }
                })
                send_message(data)
                
                # Send contact message
                contact_msg = (
                    "📞 *Contact Us:*\n\n"
                    "For Any Queries: *8800969741*\n"
                    "To Confirm and Make Payment: *7054400500*\n\n"
                    "Our team is ready to assist you! 😊"
                )
                send_message(get_text_message_input(wa_id, contact_msg))
                
            elif button_reply_id == "parivar_pravaas_btn":
                # Send Parivaar Pravas PDF
                data = json.dumps({
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": wa_id,
                    "type": "document",
                    "document": {
                        "id": "1813897679248489",
                        "caption": "Parivaar Pravaas – Stay at ease with family stays that blend comfort, privacy, and a homely touch for your perfect getaway. 🌿🏡✨",
                        "filename": "parivar_pravaas.pdf"
                    }
                })
                send_message(data)
                
                # Send contact message
                contact_msg = (
                    "🌍 Need guidance? 8800969741 \n"
                    "🎟️ Lock your seat? 7054400500\n\n"
                    "Travel dreams, one call away!\n"
                )
                send_message(get_text_message_input(wa_id, contact_msg))
                
            elif button_reply_id == "customized_tour_btn":
                # Send custom message for Customized Tour
                custom_msg = (
                    "Customized Tour – From Your City 🌟\n"
                    "Your journey, your rules. ✨\n\n"
                    "Start right from your hometown 🏠\n\n"
                    "Handpicked inclusions, made just for you 📝\n\n"
                    "Flexible itinerary 🗓️\n\n"
                    "A Dev Deepawali experience as unique as you 🌌\n\n"
                    "📞 Queries: 8800969741 | Bookings: 7054400500\n"
                    "We’ll craft the perfect celebration of lights, tailored to you. 🪔💫"
                )
                send_message(get_text_message_input(wa_id, custom_msg))
        
        # IMPORTANT: Return here to prevent any further processing
        return

    # Handle text messages - ONLY send welcome + buttons for GREETING messages
    elif message_type == "text":
        message_text = message.get("text", {}).get("body", "").strip()
        
        # Check if this is a greeting message
        if is_greeting_message(message_text):
            # Send image with caption first (replace <IMAGE_MEDIA_ID> with your actual media id)
            image_payload = json.dumps({
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": wa_id,
                "type": "image",
                "image": {
                    "id": "792434643189920",
                    "caption": f"Namaste {name}! 🙏\n\n 🌌 When the Ganga wears a thousand stars, you know it’s Dev Deepawali.Join us with HostmenIndia \n Choose Delhi departure or your city escape, and boom – itinerary at your fingertips \n\n Send 1 for -Yuva Yatra 1 – Stay carefree with separate men’s and women’s dorms plus private unattached washrooms for complete comfort, hygiene, and peace of mind.\n\n Send 2  for - Yuva Yatra 2 – Stay easy in mixed 👫 and female 👩 dorms, designed with attached washrooms 🚿 for convenience, comfort, and a relaxed journey.\n\n Send 3 for Parivaar Pravaas – Stay at ease with family stays that blend comfort, privacy, and a homely touch for your perfect getaway.\n\n Send 4 for- Customized Tour – From Your City ,Your journey, your rules. Start right from your hometown Handpicked inclusions, made just for you Flexible itinerary 🗓️\n A Dev Deepawali experience as unique as you 🌌"
                }
            })
            send_message(image_payload)

            # Send welcome message ONLY for greeting messages
            welcome_text = (
                # Add your welcome text here if needed
                ""
            )
            if welcome_text.strip():  # Only send if there's actual content
                welcome_msg = get_text_message_input(wa_id, welcome_text)
                send_message(welcome_msg)
            
            # Send tour options
            send_tour_options(wa_id)
        else:
            # For non-greeting text messages, send a different response
            help_msg = (
                f"Hello {name}! 👋\n\n"
                "I can help you with Dev Deepawali tour information. "
                "If you'd like to see our tour options again, please type 'Hi' or 'Hello'."
            )
            send_message(get_text_message_input(wa_id, help_msg))
        
        # IMPORTANT: Return here to prevent any further processing
        return

    # Handle other message types (audio, image, etc.) - Just send a simple response
    else:
        simple_msg = (
            f"Hello {name}! 👋\n\n"
            "Please send a text message to get started with our Dev Deepawali tours."
        )
        send_message(get_text_message_input(wa_id, simple_msg))
        
        # IMPORTANT: Return here to prevent any further processing  
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