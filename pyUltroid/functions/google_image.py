import random
import re
import json
from bs4 import BeautifulSoup
from . import async_searcher

async def get_google_images(query):
    soup = BeautifulSoup(
        await async_searcher(
            "https://google.com/search",
            params={"q": query, "tbm": "isch"},
            headers={"User-Agent": random.choice(some_random_headers)},
        ),
        "lxml",
    )
    google_images = []
    all_script_tags = soup.select("script")
    matched_images_data = "".join(
        re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags))
    )
    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)
    matched_google_image_data = re.findall(
        r"\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}", matched_images_data_json
    )
    matched_google_images_thumbnails = ", ".join(
        re.findall(
            r"\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]",
            str(matched_google_image_data),
        )
    ).split(", ")
    thumbnails = [
        bytes(bytes(thumbnail, "ascii").decode("unicode-escape"), "ascii").decode(
            "unicode-escape"
        )
        for thumbnail in matched_google_images_thumbnails
    ]
    removed_matched_google_images_thumbnails = re.sub(
        r"\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]",
        "",
        str(matched_google_image_data),
    )
    matched_google_full_resolution_images = re.findall(
        r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
        removed_matched_google_images_thumbnails,
    )
    full_res_images = [
        bytes(bytes(img, "ascii").decode("unicode-escape"), "ascii").decode(
            "unicode-escape"
        )
        for img in matched_google_full_resolution_images
    ]
    for index, (metadata, thumbnail, original) in enumerate(
        zip(soup.select(".isv-r.PNCib.MSM1fd.BUooTd"), thumbnails, full_res_images),
        start=1,
    ):
        google_images.append(
            {
                "title": metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")[
                    "title"
                ],
                "link": metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")[
                    "href"
                ],
                "source": metadata.select_one(".fxgdke").text,
                "thumbnail": thumbnail,
                "original": original,
            }
        )
    random.shuffle(google_images)
    return google_images
