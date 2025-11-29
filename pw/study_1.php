<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generate Access Key - VIP Study</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 100%;
            padding: 40px;
            text-align: center;
        }

        .icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }

        .icon i {
            font-size: 40px;
            color: #1e293b;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        h1 i {
            color: #FFD700;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 16px;
        }

        .info-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: left;
        }

        .info-box p {
            color: #555;
            margin-bottom: 10px;
            line-height: 1.6;
        }

        .info-box p:last-child {
            margin-bottom: 0;
        }

        .info-box strong {
            color: #333;
        }

        .status-indicator {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 20px;
        }

        .status-active {
            background: #d4edda;
            color: #155724;
        }

        .status-expired {
            background: #f8d7da;
            color: #721c24;
        }

        .generate-btn {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 30px;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .generate-btn:active {
            transform: translateY(0);
        }

        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        .back-link:hover {
            color: #764ba2;
        }

        .note {
            margin-top: 20px;
            padding: 15px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            font-size: 14px;
            color: #856404;
        }

        @media (max-width: 768px) {
            .container {
                padding: 30px 20px;
            }

            h1 {
                font-size: 24px;
            }

            .icon {
                width: 60px;
                height: 60px;
            }

            .icon i {
                font-size: 30px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">
            <i class="fas fa-crown"></i>
        </div>
        <h1><i class="fas fa-crown"></i> VIP Study - Access Key Generator</h1>
        <p class="subtitle">Generate your 48-hour access key to view study content</p>
        
                    <div class="status-indicator status-expired">
                <i class="fas fa-exclamation-circle"></i> No active key - Generate new key
            </div>
            <div class="info-box">
                <p><strong>How it works:</strong></p>
                <p>1. Click the button below to generate your access key</p>
                <p>2. You'll be redirected to watch an ad</p>
                <p>3. After viewing, you'll get 48 hours of access to study content</p>
            </div>
        
        <form method="POST">
            <button type="submit" name="generate_key" class="generate-btn">
                <i class="fas fa-magic"></i> 
                Click here to generate key
            </button>
        </form>

        <a href="../study.php" class="back-link">
            <i class="fas fa-arrow-left"></i> Back to Study Dashboard
        </a>

        <div class="note">
            <i class="fas fa-info-circle"></i> 
            <strong>Note:</strong> Each key is valid for 48 hours. After expiration, you'll need to generate a new key.
        </div>
    </div>
</body>
</html>

