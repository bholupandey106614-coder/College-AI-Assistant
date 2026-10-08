import os
import json
from datetime import date

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from pypdf import PdfReader
from docx import Document


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError(
        "HF_TOKEN not found. Please add your Hugging Face token "
        "inside the .env file."
    )


# ============================================================
# 2. HUGGING FACE CLIENT
# ============================================================

client = InferenceClient(
    api_key=HF_TOKEN
)

MODEL = "openai/gpt-oss-120b"


# ============================================================
# 3. CALCULATOR TOOL
# ============================================================

def calculate_attendance(attended, total):

    if total <= 0:
        return {
            "success": False,
            "error": "Total classes must be greater than zero."
        }

    percentage = (attended / total) * 100

    return {
        "success": True,
        "attended": attended,
        "total": total,
        "percentage": round(percentage, 2)
    }


# ============================================================
# 4. ATTENDANCE TOOL
# ============================================================

def mark_attendance(subject, status, attendance_date=None):

    if attendance_date is None:
        attendance_date = str(date.today())

    status = status.lower()

    if status not in ["present", "absent"]:
        return {
            "success": False,
            "error": "Status must be 'present' or 'absent'."
        }

    record = {
        "date": attendance_date,
        "subject": subject,
        "status": status
    }

    return {
        "success": True,
        "record": record
    }


# ============================================================
# 5. TIMETABLE TOOL
# ============================================================

def find_timetable(day, timetable):

    result = []

    for item in timetable:

        if item.get("day", "").lower() == day.lower():
            result.append(item)

    if not result:

        return {
            "success": False,
            "message": f"No classes found for {day}."
        }

    return {
        "success": True,
        "day": day,
        "classes": result
    }


# ============================================================
# 6. FILE READER
# Supports:
# PDF
# DOCX
# TXT
# ============================================================

def read_document(file_path):

    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": "File not found."
        }

    extension = os.path.splitext(file_path)[1].lower()

    try:

        # ---------------- PDF ----------------

        if extension == ".pdf":

            reader = PdfReader(file_path)

            text = ""

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            return {
                "success": True,
                "file_type": "PDF",
                "text": text
            }


        # ---------------- DOCX ----------------

        elif extension == ".docx":

            document = Document(file_path)

            text = ""

            for paragraph in document.paragraphs:

                text += paragraph.text + "\n"

            return {
                "success": True,
                "file_type": "DOCX",
                "text": text
            }


        # ---------------- TXT ----------------

        elif extension == ".txt":

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                text = file.read()

            return {
                "success": True,
                "file_type": "TXT",
                "text": text
            }


        else:

            return {
                "success": False,
                "error": "Only PDF, DOCX and TXT files are supported."
            }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# 7. TOOL DEFINITIONS FOR HUGGING FACE
# ============================================================

tools = [

    # --------------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "calculate_attendance",

            "description": (
                "Calculate attendance percentage. "
                "Use this tool whenever the student asks "
                "for attendance percentage or a numerical calculation."
            ),

            "parameters": {
                "type": "object",

                "properties": {

                    "attended": {
                        "type": "integer",
                        "description": (
                            "Number of classes attended by the student."
                        )
                    },

                    "total": {
                        "type": "integer",
                        "description": (
                            "Total number of classes."
                        )
                    }
                },

                "required": [
                    "attended",
                    "total"
                ]
            }
        }
    },


    # --------------------------------------------------------
    # ATTENDANCE
    # --------------------------------------------------------

    {
        "type": "function",

        "function": {

            "name": "mark_attendance",

            "description": (
                "Mark attendance for a particular subject and date. "
                "Use this when the student asks to mark attendance."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "subject": {
                        "type": "string",
                        "description": "Subject name."
                    },

                    "status": {
                        "type": "string",
                        "enum": [
                            "present",
                            "absent"
                        ],
                        "description": (
                            "Attendance status."
                        )
                    },

                    "attendance_date": {
                        "type": "string",
                        "description": (
                            "Date of attendance in YYYY-MM-DD format."
                        )
                    }
                },

                "required": [
                    "subject",
                    "status"
                ]
            }
        }
    },


    # --------------------------------------------------------
    # TIMETABLE
    # --------------------------------------------------------

    {
        "type": "function",

        "function": {

            "name": "find_timetable",

            "description": (
                "Find classes from the student's timetable "
                "for a particular day."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "day": {
                        "type": "string",
                        "description": (
                            "Day of the week, such as Monday."
                        )
                    }
                },

                "required": [
                    "day"
                ]
            }
        }
    }
]


# ============================================================
# 8. SAMPLE TIMETABLE
#
# Later this can be replaced with timetable extracted
# from student's PDF/DOCX/TXT.
# ============================================================

DEFAULT_TIMETABLE = [

    {
        "day": "Monday",
        "time": "09:00-10:00",
        "subject": "Data Structures"
    },

    {
        "day": "Monday",
        "time": "10:00-11:00",
        "subject": "Mathematics"
    },

    {
        "day": "Monday",
        "time": "11:00-12:00",
        "subject": "Computer Networks"
    },

    {
        "day": "Tuesday",
        "time": "09:00-10:00",
        "subject": "Python"
    },

    {
        "day": "Tuesday",
        "time": "10:00-11:00",
        "subject": "Database Management System"
    }
]


# ============================================================
# 9. EXECUTE TOOL
# ============================================================

def execute_tool(tool_name, arguments):

    # ---------------- CALCULATOR ----------------

    if tool_name == "calculate_attendance":

        return calculate_attendance(
            attended=arguments["attended"],
            total=arguments["total"]
        )


    # ---------------- ATTENDANCE ----------------

    elif tool_name == "mark_attendance":

        return mark_attendance(
            subject=arguments["subject"],
            status=arguments["status"],
            attendance_date=arguments.get("attendance_date")
        )


    # ---------------- TIMETABLE ----------------

    elif tool_name == "find_timetable":

        return find_timetable(
            day=arguments["day"],
            timetable=DEFAULT_TIMETABLE
        )


    return {
        "success": False,
        "error": "Unknown tool."
    }


# ============================================================
# 10. COLLEGE AI ASSISTANT
# ============================================================

def ask_assistant(user_input, document_text=None):

    system_prompt = """
You are a College AI Assistant.

Your job is to understand student requests and select
the correct tool.

AVAILABLE TOOLS:

1. calculate_attendance
   Use for:
   - Attendance percentage
   - Numerical attendance calculations
   - Other calculations when appropriate

2. mark_attendance
   Use when:
   - Student wants to mark attendance
   - Student wants to record present/absent
   - Student gives a subject and attendance status

3. find_timetable
   Use when:
   - Student asks about timetable
   - Student asks what classes they have
   - Student asks about classes on a particular day

IMPORTANT RULES:

- Always use a tool when the request matches a tool.
- Do not manually calculate attendance percentage.
- Use the calculator tool for attendance percentage.
- Use the attendance tool for marking attendance.
- Use the timetable tool for timetable questions.
- Always tell the student which tool was used.
- Give a clear and simple final answer.
"""

    # Add uploaded document if available

    if document_text:

        system_prompt += """

The student has uploaded a document.

Use the following document information when
answering timetable/document-related questions:

---------------- DOCUMENT ----------------

""" + document_text + """

---------------- END DOCUMENT ----------------
"""


    messages = [

        {
            "role": "system",
            "content": system_prompt
        },

        {
            "role": "user",
            "content": user_input
        }
    ]


    # ========================================================
    # FIRST LLM CALL
    # ========================================================

    response = client.chat.completions.create(

        model=MODEL,

        messages=messages,

        tools=tools,

        tool_choice="auto"
    )


    assistant_message = response.choices[0].message


    # ========================================================
    # CHECK WHETHER LLM SELECTED A TOOL
    # ========================================================

    if not assistant_message.tool_calls:

        return {
            "answer": assistant_message.content,
            "tool_used": "None"
        }


    # ========================================================
    # PROCESS TOOL CALL
    # ========================================================

    tool_call = assistant_message.tool_calls[0]

    tool_name = tool_call.function.name

    arguments = json.loads(
        tool_call.function.arguments
    )


    # ========================================================
    # EXECUTE TOOL
    # ========================================================

    tool_result = execute_tool(
        tool_name,
        arguments
    )


    # ========================================================
    # ADD TOOL RESULT TO CONVERSATION
    # ========================================================

    messages.append({

        "role": "assistant",

        "content": assistant_message.content,

        "tool_calls": [
            {
                "id": tool_call.id,

                "type": "function",

                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(arguments)
                }
            }
        ]
    })


    messages.append({

        "role": "tool",

        "tool_call_id": tool_call.id,

        "content": json.dumps(tool_result)
    })


    # ========================================================
    # SECOND LLM CALL
    # ========================================================

    final_response = client.chat.completions.create(

        model=MODEL,

        messages=messages
    )


    final_answer = final_response.choices[0].message.content


    # ========================================================
    # RETURN FINAL ANSWER
    # ========================================================

    return {

        "answer": final_answer,

        "tool_used": tool_name,

        "tool_arguments": arguments,

        "tool_result": tool_result
    }


# ============================================================
# 11. DOCUMENT UPLOAD FUNCTION
# ============================================================

def ask_with_document(user_input, file_path):

    document_result = read_document(file_path)

    if not document_result["success"]:

        return {
            "answer": document_result["error"],
            "tool_used": "Document Reader"
        }


    document_text = document_result["text"]


    return ask_assistant(
        user_input=user_input,
        document_text=document_text
    )


# ============================================================
# 12. TERMINAL APPLICATION
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("       COLLEGE AI ASSISTANT")
    print("=" * 60)

    print("\nSupported tools:")

    print("1. Calculator")
    print("2. Attendance")
    print("3. Timetable")

    print("\nSupported documents:")

    print("PDF")
    print("DOCX")
    print("TXT")

    print("\nType 'exit' to close the application.")

    print("=" * 60)


    while True:

        print("\n")

        user_input = input("Student: ").strip()


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_input.lower() == "exit":

            print("\nGoodbye!")

            break


        # ----------------------------------------------------
        # EMPTY INPUT
        # ----------------------------------------------------

        if not user_input:

            print("Please enter a question.")

            continue


        # ----------------------------------------------------
        # DOCUMENT OPTION
        # ----------------------------------------------------

        file_path = input(
            "Enter document path "
            "(press Enter if no document): "
        ).strip()


        try:

            if file_path:

                result = ask_with_document(
                    user_input,
                    file_path
                )

            else:

                result = ask_assistant(
                    user_input
                )


            # ------------------------------------------------
            # DISPLAY RESULT
            # ------------------------------------------------

            print("\n" + "-" * 60)

            print("AI Assistant:")

            print(result["answer"])

            print("\nTool Used:")

            print(result["tool_used"])

            print("-" * 60)


        except Exception as e:

            print("\nERROR:")

            print(str(e))


# ============================================================
# 13. START APPLICATION
# ============================================================

if __name__ == "__main__":

    main()
    