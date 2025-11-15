from flask import Flask, render_template_string

app = Flask(__name__)

html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aryan Sharma — Portfolio</title>

<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">

<style>
body {
    margin: 0;
    font-family: Poppins, sans-serif;
    background: #0d0017;
    color: white;
    overflow-x: hidden;
}

/* Animated Gradient Header Box */
.hero {
    width: 100%;
    padding: 80px 20px;
    text-align: center;
    border-radius: 20px;
    background: linear-gradient(120deg, #6d25ff40, #9f4dff40, #d9a7ff40);
    border: 2px solid #bb77ff40;
    backdrop-filter: blur(10px);
    animation: glow 6s infinite linear;
    margin-bottom: 40px;
}

@keyframes glow {
    0% { box-shadow: 0 0 20px #8b3dff; }
    50% { box-shadow: 0 0 40px #b96dff; }
    100% { box-shadow: 0 0 20px #8b3dff; }
}

/* Main Name */
.hero h1 {
    font-size: 52px;
    font-weight: 700;
    margin: 0;
}

/* Rotating Animation Text */
#typing {
    font-size: 20px;
    margin-top: 10px;
    color: #d9b7ff;
    font-weight: 600;
    height: 30px;
}

/* About Section */
.about {
    max-width: 900px;
    margin: auto;
    padding: 40px 20px;
    background: #ffffff05;
    border-radius: 20px;
    border: 1px solid #ffffff10;
    backdrop-filter: blur(5px);
    text-align: center;
}

.about h2 {
    font-size: 34px;
    margin-bottom: 10px;
    color: #c78fff;
}

/* Projects Section */
.projects {
    max-width: 1100px;
    margin: auto;
    padding: 50px 20px;
}

.projects h2 {
    font-size: 34px;
    margin-bottom: 25px;
    text-align: center;
    color: #c78fff;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 25px;
}

.card {
    background: #ffffff08;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #ffffff15;
    backdrop-filter: blur(6px);
    transition: 0.3s;
}

.card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 32px #a86cff40;
}

.card h3 {
    margin: 0 0 10px 0;
    font-size: 20px;
}

footer {
    text-align: center;
    padding: 20px;
    color: #aaaaaa;
    margin-top: 40px;
}
</style>
</head>

<body>

<!-- HERO HEADER WITH ANIMATION -->
<div class="hero">
    <h1>Aryan Sharma</h1>
    <div id="typing"></div>
</div>

<!-- ABOUT ME SECTION -->
<section class="about">
    <h2>About Me</h2>
    <p>
        Hi, I'm <b>Aryan Sharma</b>, currently pursuing a Bachelor's Degree.
        I'm passionate about coding, learning, and developing new things.
        This site showcases my work and lets you chat with my AI assistant
        to learn more about me.
    </p>
</section>

<!-- PROJECTS -->
<section class="projects">
    <h2>Projects</h2>

    <div class="grid">
        <div class="card">
            <h3>Chatbot Website</h3>
            <p>A chatbot-enabled website with modern UI and smooth workflows.</p>
        </div>

        <div class="card">
            <h3>Portfolio Builder</h3>
            <p>A tool that helps users generate their own portfolios instantly.</p>
        </div>

        <div class="card">
            <h3>AI Experiments</h3>
            <p>Small AI projects exploring prompts, automation & creativity.</p>
        </div>
    </div>
</section>

<footer>
    © 2025 Aryan Sharma — All Rights Reserved
</footer>

<!-- ROTATING TEXT SCRIPT -->
<script>
const roles = [
    "I'm a Web Designer",
    "I'm a Problem Solver",
    "I'm a Tech Enthusiast",
    "I'm a Developer",
    "I'm a Writer"
];

let i = 0;
let typingDiv = document.getElementById("typing");

function rotateText() {
    typingDiv.innerHTML = roles[i];
    i = (i + 1) % roles.length;
}

rotateText();
setInterval(rotateText, 2000);
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html)

if __name__ == "__main__":
    app.run(debug=True)
