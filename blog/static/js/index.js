function like(postId) {
  const likeCount = document.getElementById(`likes-count-${postId}`);
  const likeButton = document.getElementById(`like-button-${postId}`);

  fetch(`/like-post/${postId}`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      likeCount.innerHTML = data["likes"];
      if (data["liked"] === true) {
        likeButton.className = "fa-solid fa-heart";
      } else {
        likeButton.className = "fa-regular fa-heart";
      }
    })
    .catch((e) => alert("Could not like post."));
}


function comment_like(commentId) {
  const likeCount = document.getElementById(`comment-likes-count-${commentId}`);
  const likeButton = document.getElementById(`comment-like-button-${commentId}`);

  fetch(`/like-comment/${commentId}`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      likeCount.innerHTML = data["likes"];
      if (data["liked"] === true) {
        likeButton.className = "fa-solid fa-heart";
      } else {
        likeButton.className = "fa-regular fa-heart";
      }
    })
    .catch((e) => alert("Could not like comment."));
}