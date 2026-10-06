from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time

app = Flask(__name__)


def normalize_url(url):
    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def analyze_website(url):
    start_time = time.time()

    try:
        url = normalize_url(url)

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10) "
                "AppleWebKit/537.36 Chrome/120 Safari/537.36"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.get_text(strip=True) if soup.title else ""

        description_tag = soup.find(
            "meta",
            attrs={"name": re.compile("^description$", re.I)}
        )

        description = (
            description_tag.get("content", "").strip()
            if description_tag
            else ""
        )

        h1_tags = soup.find_all("h1")
        h2_tags = soup.find_all("h2")

        images = soup.find_all("img")

        images_without_alt = [
            img for img in images
            if not img.get("alt", "").strip()
        ]

        links = soup.find_all("a", href=True)

        text = soup.get_text(" ", strip=True)

        word_count = len(text.split())

        parsed = urlparse(response.url)

        secure = parsed.scheme == "https"

        # SEO score
        seo_score = 50

        if title:
            seo_score += 15

        if 30 <= len(title) <= 65:
            seo_score += 10

        if description:
            seo_score += 10

        if 100 <= len(description) <= 170:
            seo_score += 5

        if h1_tags:
            seo_score += 10

        seo_score = min(seo_score, 100)

        # Content score
        content_score = 40

        if word_count >= 300:
            content_score += 20

        if word_count >= 800:
            content_score += 20

        if h1_tags:
            content_score += 10

        if h2_tags:
            content_score += 10

        content_score = min(content_score, 100)

        # Technical score
        technical_score = 60

        if secure:
            technical_score += 20

        if response.status_code == 200:
            technical_score += 10

        if response.url == url:
            technical_score += 10

        technical_score = min(technical_score, 100)

        # Accessibility score
        accessibility_score = 100

        if images:
            missing_ratio = len(images_without_alt) / len(images)

            if missing_ratio > 0.5:
                accessibility_score -= 35
            elif missing_ratio > 0.2:
                accessibility_score -= 20
            elif missing_ratio > 0:
                accessibility_score -= 10

        if not h1_tags:
            accessibility_score -= 10

        accessibility_score = max(accessibility_score, 0)

        # Performance estimate
        load_time = round(time.time() - start_time, 2)
        performance_score = 100

        if load_time > 2:
            performance_score -= 15

        if load_time > 4:
            performance_score -= 20

        if load_time > 7:
            performance_score -= 25

        performance_score = max(performance_score, 0)

        overall = round(
            (
                seo_score
                + content_score
                + technical_score
                + accessibility_score
                + performance_score
            ) / 5
        )

        recommendations = []

        if not title:
            recommendations.append(
                "Add a unique and descriptive page title."
            )
        elif len(title) < 30:
            recommendations.append(
                "Consider making the page title more descriptive."
            )
        elif len(title) > 65:
            recommendations.append(
                "Shorten the page title so it displays better in search results."
            )

        if not description:
            recommendations.append(
                "Add a meta description for better search visibility."
            )

        if not h1_tags:
            recommendations.append(
                "Add one clear H1 heading describing the main page topic."
            )

        if images_without_alt:
            recommendations.append(
                f"Add descriptive ALT text to {len(images_without_alt)} image(s)."
            )

        if word_count < 300:
            recommendations.append(
                "Consider adding more useful, original content to the page."
            )

        if not secure:
            recommendations.append(
                "Enable HTTPS to improve security and user trust."
            )

        if load_time > 4:
            recommendations.append(
                "Improve page-loading speed by optimizing images, scripts and resources."
            )

        if not recommendations:
            recommendations.append(
                "No major basic issues detected. Continue improving content quality and conversion optimization."
            )

        return {
            "success": True,
            "url": response.url,
            "domain": parsed.netloc,
            "title": title,
            "description": description,
            "overall_score": overall,
            "scores": {
                "seo": seo_score,
                "content": content_score,
                "technical": technical_score,
                "accessibility": accessibility_score,
                "performance": performance_score
            },
            "statistics": {
                "word_count": word_count,
                "h1_count": len(h1_tags),
                "h2_count": len(h2_tags),
                "image_count": len(images),
                "images_without_alt": len(images_without_alt),
                "link_count": len(links),
                "response_time": load_time
            },
            "recommendations": recommendations
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "The website took too long to respond."
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Could not access the website: {str(e)}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis error: {str(e)}"
        }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}

    url = data.get("url", "").strip()

    if not url:
        return jsonify({
            "success": False,
            "error": "Please enter a website URL."
        }), 400

    result = analyze_website(url)

    return jsonify(result)


if __name__ == "__main__":
    print("")
    print("======================================")
    print("       KEEN CORTEX PRO")
    print("       Website AI Analyzer")
    print("======================================")
    print("")
    print("Open in your browser:")
    print("http://127.0.0.1:5000")
    print("")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
