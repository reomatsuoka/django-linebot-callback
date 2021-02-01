from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)

class CallbackView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('ko')

    def post(self, request, *args, **kwargs):
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            # 署名を検証して、問題なければhandleに定義されている関数を呼び出す
            handler.handle(body, signature)
        except InvalidSignatureError:
            # 署名検証で失敗した場合は、例外をあげる
            return HttpResponseBadRequest()
        except LineBotApiError as e:
            # APIのエラーが発生した場合は、例外をあげる
            print(e)
            return HttpResponseServerError()

        return HttpResponse('OK')

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CallbackView, self).dispatch(*args, **kwargs)

    @staticmethod
    @handler.add(MessageEvent, message=TextMessage)
    def message_event(event):

        reply = event.message.text

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )