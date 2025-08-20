document.addEventListener('DOMContentLoaded', function() {
    // モーダル要素を取得
    var modal = document.getElementById("graphModal");
    var modalImg = document.getElementById("modalImage");
    var closeButton = document.querySelector(".close-button");

    // モーダルを開くための画像要素のIDリスト
    var graphIds = [
        "points-24-25-graph",
        "attempts-24-25-graph",
        "points-23-24-graph",
        "attempts-23-24-graph"
    ];

    // 各画像にクリックイベントを設定
    graphIds.forEach(function(id) {
        var graph = document.getElementById(id);
        if (graph) {
            graph.onclick = function() {
                modal.style.display = "block";
                modalImg.src = this.src;
            }
        }
    });

    // モーダルを閉じるイベント
    if(closeButton) {
        closeButton.onclick = function() {
            modal.style.display = "none";
        }
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});