# 設定 Dockerfile 的路徑
$dbDockerfilePath = "C:\Users\seans\codewhitelist\gdg\MonkeyWatchCopy\server\db.dockerfile"
$webDockerfilePath = "C:\Users\seans\codewhitelist\gdg\MonkeyWatchCopy\server\web.dockerfile"

# 設定 Docker image 的名稱
$dbImageName = "monkeywatch-db"
$webImageName = "monkeywatch-web"

# 建置 db image
docker build -t $dbImageName -f $dbDockerfilePath .

# 執行 db container
docker run -d --name monkeywatch-db-container $dbImageName

# 建置 web image
docker build -t $webImageName -f $webDockerfilePath .

# 執行 web container，並連結到 db container
docker run -d --name monkeywatch-web-container --link monkeywatch-db-container:db $webImageName