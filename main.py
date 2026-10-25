import html
import json
import math

import streamlit as st


PARTY_MEMBERS = (
    "Panda",
    "Batman",
    "Sensei",
    "Indu",
    "Sensei Wife",
    "Ayush",
    "Divyanshu",
    "Mayur",
    "Kaustubh",
    "Nick",
    "Anusha",
)
SEGMENT_COLORS = (
    "#ef476f",
    "#118ab2",
    "#f4a261",
    "#06a77d",
    "#8f5bd7",
    "#e76f51",
    "#287271",
    "#e9c46a",
    "#4361ee",
    "#d45087",
    "#4d908e",
)

st.set_page_config(page_title="Sabko Aana Hai", page_icon="🎉", layout="centered")

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(ellipse at 50% 5%, rgba(116, 80, 210, .48), transparent 48%),
                linear-gradient(145deg, #11142b 0%, #1e1b42 52%, #301c4b 100%);
            color: #fff;
        }
        [data-testid="stMainBlockContainer"] { padding-top: 1.5rem; }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stMain"] { background: transparent; }
        .hero { text-align: center; padding: .8rem 0 .45rem; }
        .hero h1 {
            color: #fff;
            font-size: clamp(2rem, 6vw, 2.8rem);
            letter-spacing: -.04em;
            margin: 0 0 .55rem;
        }
        .hero p { color: #d7d3ed; font-size: 1.08rem; margin: 0; }
        div[data-testid="stForm"] {
            background: rgba(255,255,255,.07);
            border: 1px solid rgba(255,255,255,.14);
            border-radius: 22px;
            padding: 1.25rem;
        }
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            min-height: 3rem;
            border: 0;
            border-radius: 999px;
            background: linear-gradient(135deg, #ffd166, #fca311);
            color: #241a36;
            font-weight: 800;
            letter-spacing: .04em;
            box-shadow: 0 8px 24px rgba(252,163,17,.22);
            transition: transform .18s ease, box-shadow .18s ease;
        }
        div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
            color: #241a36;
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(252,163,17,.35);
        }
        [data-testid="stTextInput"] input {
            background: rgba(255,255,255,.96);
            border-radius: 12px;
        }
        .welcome { text-align: center; color: #e6e1f5; margin: .35rem 0 0; }
        .note { text-align: center; color: #c9c4dd; font-size: .92rem; margin: .15rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🎉 Sabko Aana Hai 🎉</h1>
        <p>One spin. One party pairing. Let fate decide.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def eligible_members(visitor_name: str) -> list[str]:
    """Return party members other than the visitor, ignoring letter case."""
    normalized_name = visitor_name.strip().casefold()
    return [
        member for member in PARTY_MEMBERS
        if member.casefold() != normalized_name
    ]


def wheel_html(members: list[str], visitor_name: str) -> str:
    """Build the SVG wheel and its one-time spin animation."""
    center = 260
    radius = 245
    label_radius = 158
    slice_angle = 360 / len(members)
    sectors: list[str] = []
    labels: list[str] = []

    for index, member in enumerate(members):
        start_angle = -90 + index * slice_angle
        end_angle = start_angle + slice_angle
        middle_angle = (start_angle + end_angle) / 2
        start_radians = math.radians(start_angle)
        end_radians = math.radians(end_angle)
        start_x = center + radius * math.cos(start_radians)
        start_y = center + radius * math.sin(start_radians)
        end_x = center + radius * math.cos(end_radians)
        end_y = center + radius * math.sin(end_radians)
        large_arc = 1 if slice_angle > 180 else 0
        sectors.append(
            f'<path id="slice-{index}" class="slice" '
            f'd="M {center} {center} L {start_x:.2f} {start_y:.2f} '
            f'A {radius} {radius} 0 {large_arc} 1 {end_x:.2f} {end_y:.2f} Z" '
            f'fill="{SEGMENT_COLORS[index % len(SEGMENT_COLORS)]}" />'
        )

        label_x = center + label_radius * math.cos(math.radians(middle_angle))
        label_y = center + label_radius * math.sin(math.radians(middle_angle))
        label_rotation = middle_angle + 90
        normalized_rotation = label_rotation % 360
        if 90 < normalized_rotation < 270:
            label_rotation += 180
        labels.append(
            f'<g transform="translate({label_x:.2f} {label_y:.2f}) '
            f'rotate({label_rotation:.2f})">'
            f'<text class="wheel-label" text-anchor="middle" '
            f'transform="rotate(0)">{html.escape(member)}</text></g>'
        )

    members_json = json.dumps(members).replace("<", "\\u003c")
    rotation_script = f"""
        const candidates = {members_json};
        const wheel = document.getElementById("wheel");
        const spinButton = document.getElementById("spin-button");
        const status = document.getElementById("spin-status");
        const result = document.getElementById("result");
        const buddyName = document.getElementById("buddy-name");
        let hasSpun = false;

        function startSpin() {{
            if (hasSpun) return;
            hasSpun = true;
            spinButton.disabled = true;
            spinButton.innerHTML = "SPINNING";
            status.textContent = "Spinning... your party pairing is on its way!";

            const selectedIndex = Math.floor(Math.random() * candidates.length);
            const selectedMember = candidates[selectedIndex];
            const selectedSlice = document.getElementById(`slice-${{selectedIndex}}`);
            const labels = document.querySelectorAll(".wheel-label");
            const sliceAngle = 360 / candidates.length;
            const rotation = 6 * 360 +
                ((360 - ((selectedIndex + 0.5) * sliceAngle)) % 360);
            buddyName.textContent = selectedMember;

            function finishSpin() {{
                status.textContent = "The wheel has spoken!";
                spinButton.textContent = "DONE!";
                selectedSlice.classList.add("winner");
                result.setAttribute("aria-hidden", "false");
                result.classList.add("visible");
            }}

            if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {{
                wheel.style.transform = `rotate(${{rotation}}deg)`;
                labels.forEach((label) => {{
                    label.setAttribute("transform", `rotate(${{-rotation}})`);
                }});
                finishSpin();
                return;
            }}

            const duration = 6000;
            const startTime = performance.now();
            function animate(now) {{
                const progress = Math.min((now - startTime) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 5);
                const angle = rotation * eased;
                wheel.style.transform = `rotate(${{angle}}deg)`;
                labels.forEach((label) => {{
                    label.setAttribute("transform", `rotate(${{-angle}})`);
                }});
                if (progress < 1) {{
                    requestAnimationFrame(animate);
                }} else {{
                    finishSpin();
                }}
            }}
            requestAnimationFrame(animate);
        }}

        spinButton.addEventListener("click", startSpin);
    """
    result_markup = f"""
        <section id="result" class="result" aria-live="polite" aria-hidden="true">
            <div class="result-card">
                <div class="celebration">🎊</div>
                <p>{html.escape(visitor_name)}, you've been paired with</p>
                <h2 id="buddy-name"></h2>
                <strong>Enjoy the party! 🥳</strong>
            </div>
        </section>
    """
    return f"""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * {{ box-sizing: border-box; }}
                body {{
                    margin: 0;
                    color: #fff;
                    background: transparent;
                    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                        BlinkMacSystemFont, "Segoe UI", sans-serif;
                    text-align: center;
                }}
                .wheel-stage {{
                    width: min(100%, 440px);
                    margin: 0 auto;
                    padding: 18px 16px 0;
                }}
                .wheel-wrap {{
                    position: relative;
                    width: 100%;
                    aspect-ratio: 1;
                    margin: 0 auto;
                    filter: drop-shadow(0 18px 24px rgba(0,0,0,.38));
                }}
                .wheel {{
                    display: block;
                    width: 100%;
                    height: 100%;
                    overflow: visible;
                    transform: rotate(0deg);
                    transform-origin: center;
                    will-change: transform;
                }}
                .slice {{
                    stroke: rgba(255,255,255,.9);
                    stroke-width: 2.5;
                    stroke-linejoin: round;
                    transition: filter .25s ease;
                }}
                .slice.winner {{ stroke: #fff5c2; stroke-width: 6; }}
                .wheel-label {{
                    fill: #fff;
                    font-size: 13px;
                    font-weight: 800;
                    paint-order: stroke;
                    stroke: rgba(21,18,43,.58);
                    stroke-width: 2.4px;
                    stroke-linejoin: round;
                    pointer-events: none;
                }}
                .pointer {{
                    position: absolute;
                    z-index: 2;
                    top: 8px;
                    left: 50%;
                    width: 0;
                    height: 0;
                    transform: translateX(-50%);
                    border-left: 17px solid transparent;
                    border-right: 17px solid transparent;
                    border-top: 34px solid #fff;
                    filter: drop-shadow(0 3px 5px rgba(0,0,0,.5));
                }}
                .center-cap {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    display: grid;
                    place-items: center;
                    width: 90px;
                    height: 90px;
                    transform: translate(-50%,-50%);
                    border: 5px solid rgba(255,255,255,.92);
                    border-radius: 50%;
                    background: radial-gradient(circle at 35% 30%, #fff6cf, #ffc857 60%, #ed9b16);
                    box-shadow: 0 5px 15px rgba(0,0,0,.3), inset 0 2px 5px #fff9;
                    color: #38274d;
                    font: 900 1rem/1.15 Inter, ui-sans-serif, system-ui, sans-serif;
                    cursor: pointer;
                }}
                .center-cap:hover:not(:disabled) {{
                    filter: brightness(1.08);
                    box-shadow: 0 7px 20px rgba(0,0,0,.35), inset 0 2px 5px #fff9;
                }}
                .center-cap:disabled {{
                    cursor: default;
                    opacity: .9;
                }}
                #spin-status {{
                    min-height: 1.5rem;
                    margin: 8px 0 14px;
                    color: #e6e1f5;
                    font-size: .96rem;
                }}
                .result {{
                    position: fixed;
                    z-index: 5;
                    inset: 0;
                    display: grid;
                    place-items: center;
                    padding: 1rem;
                    background: rgba(17,20,43,.74);
                    backdrop-filter: blur(6px);
                    opacity: 0;
                    visibility: hidden;
                    transform: scale(.97);
                    transition: opacity .5s ease, transform .5s cubic-bezier(.2,.8,.2,1),
                        visibility .5s;
                    pointer-events: none;
                }}
                .result.visible {{
                    opacity: 1;
                    visibility: visible;
                    transform: scale(1);
                }}
                .result-card {{
                    background: linear-gradient(145deg, rgba(255,255,255,.12), rgba(255,255,255,.06));
                    border: 1px solid rgba(255,255,255,.2);
                    border-radius: 22px;
                    padding: 1rem 1.25rem;
                    box-shadow: 0 16px 40px rgba(0,0,0,.25);
                }}
                .result-card p {{ margin: 0; color: #e9e5f6; }}
                .result-card h2 {{
                    color: #ffd166;
                    font-size: clamp(1.8rem, 5vw, 2.5rem);
                    margin: .15rem 0 .25rem;
                }}
                .result-card strong {{ color: #fff; }}
                .celebration {{ font-size: 1.7rem; }}
                .slice.winner {{ filter: drop-shadow(0 0 9px #fff); }}
                @media (max-width: 420px) {{
                    .wheel-stage {{ padding: 10px 6px 0; }}
                    .pointer {{ top: 3px; }}
                    .center-cap {{ width: 66px; height: 66px; font-size: .8rem; }}
                    .wheel-label {{ font-size: 14px; }}
                }}
            </style>
        </head>
        <body>
            <main class="wheel-stage">
                <div class="wheel-wrap">
                    <div class="pointer" aria-hidden="true"></div>
                    <svg id="wheel" class="wheel" viewBox="0 0 520 520"
                         role="img" aria-label="Party pairing wheel">
                        <circle cx="260" cy="260" r="253" fill="#17152e"
                                stroke="rgba(255,255,255,.82)" stroke-width="5" />
                        {''.join(sectors)}
                        {''.join(labels)}
                        <circle cx="260" cy="260" r="245" fill="none"
                                stroke="rgba(255,255,255,.68)" stroke-width="3" />
                    </svg>
                    <button id="spin-button" class="center-cap" type="button">
                        TAP<br>TO SPIN
                    </button>
                </div>
                <p id="spin-status">Tap the center button to spin the wheel</p>
                {result_markup}
            </main>
            <script>{rotation_script}</script>
        </body>
        </html>
    """


if "visitor_name" not in st.session_state:
    st.session_state.visitor_name = None

if st.session_state.visitor_name is None:
    with st.form("join_party"):
        name_input = st.text_input(
            "Your name",
            placeholder="Type your name here",
            max_chars=40,
        )
        joined = st.form_submit_button("Join the party 🎊", use_container_width=True)

    if joined:
        clean_name = name_input.strip()
        if clean_name:
            st.session_state.visitor_name = clean_name
            st.rerun()
        else:
            st.warning("Please enter your name to join the party.")
else:
    visitor_name = st.session_state.visitor_name
    candidates = eligible_members(visitor_name)
    st.markdown(
        f'<p class="welcome">Welcome, {html.escape(visitor_name)}! '
        "Your party pairing awaits.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="note">The wheel shows every possible pairing. '
        "You won't be paired with yourself.</p>",
        unsafe_allow_html=True,
    )

    st.iframe(
        wheel_html(candidates, visitor_name),
        height=650,
        width="stretch",
        alt="Party pairing wheel with the eligible party members",
    )