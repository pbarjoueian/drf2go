"""
Simple WebSocket consumer example.

This module contains a basic WebSocket consumer for demonstration.
"""

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class SimpleConsumer(AsyncWebsocketConsumer):
    """
    Simple WebSocket consumer that echoes messages back to the client.

    Example usage:
        Connect to: ws://localhost:8000/ws/simple/
        Send: {"message": "Hello"}
        Receive: {"message": "Hello"}
    """

    async def connect(self):
        """Handle WebSocket connection."""
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection",
                    "message": "Connected successfully",
                }
            )
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        pass

    async def receive(self, text_data):
        """Handle message received from WebSocket."""
        try:
            data = json.loads(text_data)
            message = data.get("message", "")

            # Echo the message back
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "message",
                        "message": f"Echo: {message}",
                    }
                )
            )
        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                    }
                )
            )
