import asyncio
from flask import Flask, render_template, request, jsonify, Response
from .scraper import scrape_profile_page, ProfileNotFoundException, ProfileIsPrivateException, ScrapeTimeoutException
from .utils import download_images_as_bytes, create_zip_in_memory

app = Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    username = data.get('username')

    if not username or not isinstance(username, str) or ' ' in username:
        return jsonify({'error': '유효하지 않은 계정명입니다.'}), 400
    
    try:
        # 1. 스크래핑(비동기 함수 실행)
        image_urls = asyncio.run(scrape_profile_page(username))
        if not image_urls:
            return jsonify({'error': '다운로드할 이미지를 찾을 수 없습니다.'}), 404
        
        # 2. 이미지 다운로드(비동기 함수 실행)
        image_data = asyncio.run(download_images_as_bytes(image_urls))
        if not image_data:
            return jsonify({'error': '이미지를 다운로드하는 데 실패했습니다.'}), 500
        
        # 3. ZIP 파일로 압축
        zip_bytes = create_zip_in_memory(image_data)

        # 4. ZIP 파일 응답 생성
        return Response(
            zip_bytes,
            mimetype='application/zip',
            headers={'Content-Disposition':
            f'attachment;filename={username}_instagram_photos.zip'}
        )
    
    except ProfileNotFoundException as e:
        return jsonify({'error': f"'{username}' 계정을 찾을 수 없습니다."}), 404
    except ProfileIsPrivateException as e:
        return jsonify({'error': f"'{username}' 계정은 비공개이거나 게시물이 없습니다."}), 403
    except ScrapeTimeoutException as e:
        return jsonify({'error': '인스타그램에서 응답이 없어 시간 초과되었습니다. 잠시 후 다시 시도해주세요.'}), 408 # 408 Request Timeout
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        return jsonify({'error': '알 수 없는 오류가 발생했습니다. 서버 로그를 확인하세요.'}), 500
    

if __name__ == '__main__':
    app.run(debug=True)