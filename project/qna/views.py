# MESSAGES AND SHORTCUT IMPORT
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse

from app.models import *
from bson import ObjectId
from bson import json_util
import json
from django.core.mail import EmailMultiAlternatives
from threading import Thread
from datetime import datetime

# QNA PAGE
def qna(request):
    # if "user_id" not in request.session and (not request.GET.get("from")):
    #     return redirect("login")
    
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        question = QnA(
            title=title,
            content=content,
            posted_by=ObjectId(request.session.get("user_id")),
        )
        question.save()

    questions = QnA.objects()
    modified_ques = []
    if len(questions) > 0:
        for question in questions:
            userId = ObjectId(question.posted_by.id)
            user = User.objects.get(id=userId)
            que_dict = question.to_mongo().to_dict()
            que_dict["username"] = user.username
            que_dict["id"] = str(question.id)
            modified_ques.append(que_dict)

    if request.GET.get("from") == "js":
        if not request.GET.get("uid"):
            return redirect("login")
        else:
            obj_id = ObjectId(request.GET.get("qid"))
            que = QnA.objects.get(id=obj_id)
            answers = que.answers
            data = []
            for ans in answers:
                ans_dict = {}
                ans_dict["id"] = ans.id
                ans_dict["created_at"] = ans.created_at
                ans_dict["username"] = ans.created_by.username
                ans_dict["content"] = ans.answer_body
                data.append(ans_dict)
            return JsonResponse(json_util.dumps(data), safe=False)
    return render(request, "qna.html", {"questions": reversed(modified_ques)})

# ANSWER QUESTION
def que_answer(request):
    data = json.loads(request.body)["data"]
    if "uid" not in data:
        return redirect("login")
    answer_body = data["content"]
    created_by = ObjectId(data["uid"])
    for_question = ObjectId(data["qid"])
    answer_body = data["content"]
    answer = Answer(
        answer_body=answer_body, created_by=created_by, for_question=for_question
    )
    answer.save()
    question = QnA.objects.get(id=for_question)
    question.answers.append(answer)
    question.save()

    if question.posted_by.notifications:
        subject = "🎉 Someone answered to your asked question on Python World!"
        from_email = "your_email@gmail.com"
        to_email = [question.posted_by.email]
    

        html_content = f"""
             <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Python World Notification</title>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                    
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    
                    body {{
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background-color: #0f172a;
                        color: #e2e8f0;
                        line-height: 1.6;
                        padding: 20px;
                    }}
                    
                    .email-container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                        border-radius: 16px;
                        overflow: hidden;
                        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                    }}
                    
                    .email-header {{
                        background: linear-gradient(135deg, #3498db, #6366f1);
                        padding: 2rem;
                        text-align: center;
                        position: relative;
                        overflow: hidden;
                    }}
                    
                    .email-header::before {{
                        content: '';
                        position: absolute;
                        top: -50%;
                        left: -50%;
                        width: 200%;
                        height: 200%;
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                        animation: shimmer 3s ease-in-out infinite;
                    }}
                    
                    @keyframes shimmer {{
                        0%, 100% {{ transform: rotate(0deg); }}
                        50% {{ transform: rotate(180deg); }}
                    }}
                    
                    .logo {{
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 0.5rem;
                        font-weight: 700;
                        font-size: 1.8rem;
                        color: white;
                        margin-bottom: 0.5rem;
                        position: relative;
                        z-index: 2;
                        color:rgb(9, 55, 147);
                    }}
                    
                    .logo span {{
                        color:rgb(9, 140, 53);
                    }}
                    
                    .notification-icon {{
                        font-size: 2.5rem;
                        margin-bottom: 1rem;
                        position: relative;
                        z-index: 2;
                    }}
                    
                    .email-body {{
                        padding: 2rem;
                    }}
                    
                    .notification-card {{
                        background-color: rgba(30, 41, 59, 0.6);
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin-bottom: 1.5rem;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                    }}
                    
                    .greeting {{
                        font-size: 1.1rem;
                        margin-bottom: 1rem;
                        color: #e2e8f0;
                    }}
                    
                    .notification-content {{
                        background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(99, 102, 241, 0.1));
                        border-left: 4px solid #3498db;
                        padding: 1rem;
                        border-radius: 8px;
                        margin: 1rem 0;
                    }}
                    
                    .notification-text {{
                        font-size: 1rem;
                        margin-bottom: 0.5rem;
                    }}
                    
                    .post-title {{
                        color: #3498db;
                        font-weight: 600;
                        font-style: italic;
                    }}
                    
                    .username {{
                        color: #2ecc71;
                        font-weight: 600;
                    }}
                    
                    .cta-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #3498db, #6366f1);
                        color: white;
                        padding: 0.8rem 1.5rem;
                        border-radius: 50px;
                        text-decoration: none;
                        font-weight: 600;
                        margin: 1rem 0;
                        transition: transform 0.2s, box-shadow 0.2s;
                        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
                    }}
                    
                    .cta-button:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
                    }}
                    
                    .email-footer {{
                        background-color: #020617;
                        padding: 1.5rem 2rem;
                        text-align: center;
                        border-top: 1px solid rgba(255, 255, 255, 0.05);
                    }}
                    
                    .footer-text {{
                        font-size: 0.85rem;
                        color: #94a3b8;
                        margin-bottom: 0.5rem;
                    }}
                    
                    .social-links {{
                        display: flex;
                        justify-content: center;
                        gap: 1rem;
                        margin-top: 1rem;
                    }}
                    
                    .social-links a {{
                        width: 36px;
                        height: 36px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: rgba(30, 41, 59, 0.5);
                        border-radius: 50%;
                        color: #94a3b8;
                        text-decoration: none;
                        transition: all 0.3s ease;
                    }}
                    
                    .social-links a:hover {{
                        background: #3498db;
                        color: white;
                        transform: translateY(-2px);
                    }}
                    
                    .divider {{
                        height: 1px;
                        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                        margin: 1.5rem 0;
                    }}
                    
                    /* Responsive */
                    @media (max-width: 600px) {{
                        .email-container {{
                            margin: 10px;
                            border-radius: 12px;
                        }}
                        
                        .email-header, .email-body {{
                            padding: 1.5rem;
                        }}
                        
                        .logo {{
                            font-size: 1.5rem;
                        }}
                        
                        .notification-icon {{
                            font-size: 2rem;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-header">
                        <div class="logo">
                           <pre>Python<span> World</span></pre>
                        </div>
                        <br>
                        <p style="color:white">Where you can ask questions and get answers</p>
                    </div>
                    
                    <div class="email-body">
                        <div class="notification-card">
                            <div class="greeting">
                                Hi <span class="username">{question.posted_by.username}</span>,
                            </div>
                            
                            <div class="notification-content">
                                <div class="notification-text" style="color: white;">
                                    <strong class="username">Someone</strong> answered to your asked question titled: 
                                    <span class="post-title">"{question.title}"</span>
                                </div>
                            </div>
                            
                            <p style="color: #94a3b8; margin-bottom: 1rem;">
                                Your content is making an impact in the Python community! 🐍
                            </p>
                            
                            <a href="pythonworld.mooo.com/qna/{question.id}" class="cta-button" style="color:white">
                                View Your question
                            </a>
                        </div>
                        
                        <div class="divider"></div>
                        
                        <div style="text-align: center;">
                            <p style="color: #94a3b8; font-size: 0.9rem;">
                                Keep sharing your knowledge and connecting with fellow developers!
                            </p>
                        </div>
                    </div>
                    
                    <div class="email-footer">
                        <p class="footer-text">
                            This is an automatic notification from Python World
                        </p>
                        <p class="footer-text">
                            © 2025 Python World. All rights reserved.
                        </p>
                        
                    </div>
                </div>
            </body>
            </html>

            """

                # Plain text fallback
        text_content = f"""
                        Hi {question.posted_by.username},

                        Someone answered to your asked question titled: "{question.title}"

                        Your content is making an impact in the Python community!

                        Check it out on your profile!

                        ---
                        This is an automatic notification from Python World.
                        © 2025 Python World. All rights reserved.
                        """

        try:
            send_email_async(subject, text_content, html_content, from_email, to_email, question)
        except Exception as e:
            print(f"Failed to send email: {str(e)}")





    ans_dict = {
        "id": answer.id,
        "created_at": answer.created_at,
        "username": answer.created_by.username,
        "content": answer.answer_body,
    }
    return JsonResponse({"msg": json_util.dumps(ans_dict)})

    data = json.loads(request.body)["data"]
    if "uid" not in data:
        return redirect("login")
    answer_body = data["content"]
    created_by = ObjectId(data["uid"])
    for_question = ObjectId(data["qid"])
    answer_body = data["content"]
    answer = Answer(
        answer_body=answer_body, created_by=created_by, for_question=for_question
    )
    answer.save()
    question = QnA.objects.get(id=for_question)
    question.answers.append(answer)
    question.save()
    ans_dict = {
        "id": answer.id,
        "created_at": answer.created_at,
        "username": answer.created_by.username,
        "content": answer.answer_body,
    }
    return JsonResponse({"msg": json_util.dumps(ans_dict)})

# UPVOTE QUESTION
def upvote_que(request,que_id):
    qid = ObjectId(que_id)
    question = QnA.objects.get(id=qid)
    
    user = User.objects.get(id=ObjectId(request.session.get("user_id")))
    if user in question.upvotes:
        question.upvotes.remove(user)
        status = "removed"
        
    else:
        if user in question.downvotes:
            question.downvotes.remove(user)
        question.upvotes.append(user)
        status = "added"
    question.save()


    
    if question.posted_by.notifications:
        subject = "🎉 Someone upvoted your asked question on Python World!"
        from_email = "your_email@gmail.com"
        to_email = [question.posted_by.email]
    
        html_content = f"""
        <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Python World Notification</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #0f172a;
                color: #e2e8f0;
                line-height: 1.6;
                padding: 20px;
            }}

            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            .email-header {{
                background: linear-gradient(135deg, #3498db, #6366f1);
                padding: 2rem;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}

            .email-header::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: shimmer 3s ease-in-out infinite;
            }}

            @keyframes shimmer {{
                0%, 100% {{ transform: rotate(0deg); }}
                50% {{ transform: rotate(180deg); }}
            }}

            .logo {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                font-weight: 700;
                font-size: 1.8rem;
                color: white;
                margin-bottom: 0.5rem;
                position: relative;
                z-index: 2;
                color:rgb(9, 55, 147);
            }}

            .logo span {{
                color:rgb(9, 140, 53);
            }}

            .notification-icon {{
                font-size: 2.5rem;
                margin-bottom: 1rem;
                position: relative;
                z-index: 2;
            }}

            .email-body {{
                padding: 2rem;
            }}

            .notification-card {{
                background-color: rgba(30, 41, 59, 0.6);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
            }}

            .greeting {{
                font-size: 1.1rem;
                margin-bottom: 1rem;
                color: #e2e8f0;
            }}

            .notification-content {{
                background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(99, 102, 241, 0.1));
                border-left: 4px solid #3498db;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            }}

            .notification-text {{
                font-size: 1rem;
                margin-bottom: 0.5rem;
            }}

            .post-title {{
                color: #3498db;
                font-weight: 600;
                font-style: italic;
            }}

            .username {{
                color: #2ecc71;
                font-weight: 600;
            }}

            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #3498db, #6366f1);
                color: white;
                padding: 0.8rem 1.5rem;
                border-radius: 50px;
                text-decoration: none;
                font-weight: 600;
                margin: 1rem 0;
                transition: transform 0.2s, box-shadow 0.2s;
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
            }}

            .cta-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
            }}

            .email-footer {{
                background-color: #020617;
                padding: 1.5rem 2rem;
                text-align: center;
                border-top: 1px solid rgba(255, 255, 255, 0.05);
            }}

            .footer-text {{
                font-size: 0.85rem;
                color: #94a3b8;
                margin-bottom: 0.5rem;
            }}

            .social-links {{
                display: flex;
                justify-content: center;
                gap: 1rem;
                margin-top: 1rem;
            }}

            .social-links a {{
                width: 36px;
                height: 36px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(30, 41, 59, 0.5);
                border-radius: 50%;
                color: #94a3b8;
                text-decoration: none;
                transition: all 0.3s ease;
            }}

            .social-links a:hover {{
                background: #3498db;
                color: white;
                transform: translateY(-2px);
            }}

            .divider {{
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                margin: 1.5rem 0;
            }}

            @media (max-width: 600px) {{
                .email-container {{
                    margin: 10px;
                    border-radius: 12px;
                }}
                .email-header, .email-body {{
                    padding: 1.5rem;
                }}
                .logo {{
                    font-size: 1.5rem;
                }}
                .notification-icon {{
                    font-size: 2rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <div class="logo">
                    <pre>Python<span> World</span></pre>
                </div>
                <br>
                <p style="color:white">Where Pythonistas meet Pythonistas</p>
            </div>

            <div class="email-body">
                <div class="notification-card">
                    <div class="greeting">
                        Hi <span class="username">{question.posted_by.username}</span>,
                    </div>

                    <div class="notification-content">
                        <div class="notification-text" style="color:white">
                            <strong class="username">Someone</strong> upvoted your post titled:
                            <span class="post-title">"{question.title}"</span>
                        </div>
                    </div>

                    <p style="color: #94a3b8; margin-bottom: 1rem;">
                        Your content is making an impact in the Python community! 🐍
                    </p>

                    <a href="pythonworld.mooo.com/profile/{user.username}" class="cta-button" style="color:white">
                        View Your Question
                    </a>
                </div>

                <div class="divider"></div>

                <div style="text-align: center;">
                    <p style="color: #94a3b8; font-size: 0.9rem;">
                        Keep sharing your knowledge and connecting with fellow developers!
                    </p>
                </div>
            </div>

            <div class="email-footer">
                <p class="footer-text">
                    This is an automatic notification from Python World
                </p>
                <p class="footer-text">
                    © 2025 Python World. All rights reserved.
                </p>

            </div>
        </div>
    </body>
    </html>

    """


    # Plain text fallback
        text_content = f"""
            Hi {question.posted_by.username},
            Someone liked your post titled: "{question.title}"
            Your content is making an impact in the Python community!
            Check it out on your profile!
            ---
            This is an automatic notification from Python World.
            © 2025 Python World. All rights reserved.
            """

        try:
            send_email_async(subject, text_content, html_content, from_email, to_email, question)
        except Exception as e:
            print(f"Failed to send email: {str(e)}")



    return JsonResponse({
            "status":status,
            "upvotes": len(question.upvotes),
            "downvotes": len(question.downvotes),
        })


# DOWNVOTE QUESTION
def downvote_que(request,que_id):
    qid = ObjectId(que_id)
    question = QnA.objects.get(id=qid)
    user = User.objects.get(id=ObjectId(request.session.get("user_id")))
    if user in question.downvotes:
        question.downvotes.remove(user)
        status = "removed"
    else:
        if user in question.upvotes:
            question.upvotes.remove(user)
        question.downvotes.append(user)
        status = "added"
    question.save()
    return JsonResponse({
            "status":status,
            "upvotes": len(question.upvotes),
            "downvotes": len(question.downvotes),
        })

# SEND MAIL ASYNC
def send_email(subject, text_content, html_content, from_email, to_email, post):
    try:
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        print(f"Email sent successfully to {post.posted_by.email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def send_email_async(subject, text_content, html_content, from_email, to_email, post):
    Thread(target=send_email, args=(subject, text_content, html_content, from_email, to_email, post)).start()