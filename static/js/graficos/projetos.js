document.addEventListener("DOMContentLoaded", () => {

  fetch("/listar_projetos")
    .then(r => r.json())
    .then(data => {

      const tbody = document.getElementById("links-body");
      tbody.innerHTML = "";

      let html = "";

      (data.projetos || []).forEach(p => {

        html += "<tr>";

        if (p.link_tiktok && p.link_tiktok !== "null") {

          html += `
            <td>
              <a href="${p.link_tiktok}" target="_blank"
                style="
                  display:inline-block;
                  width:32px;
                  height:32px;
                  border-radius:20%;
                  background-image:url('/static/img/tik-tok.svg');
                  background-repeat:no-repeat;
                  background-position:center;
                  background-size:cover;
                ">
              </a>
            </td>`;
        }

        if (p.link_youtube && p.link_youtube !== "null") {

          html += `
            <td>
              <a href="${p.link_youtube}" target="_blank"
                style="
                  display:inline-block;
                  width:32px;
                  height:32px;
                  border-radius:20%;
                  background-image:url('/static/img/youtube1.svg');
                  background-repeat:no-repeat;
                  background-position:center;
                  background-size:cover;
                ">
              </a>
            </td>`;
        }

        if (p.link_instagram && p.link_instagram !== "null") {

          html += `
            <td>
              <a href="${p.link_instagram}" target="_blank"
                style="
                  display:inline-block;
                  width:32px;
                  height:32px;
                  border-radius:20%;
                  background-image:url('https://res.cloudinary.com/dptprh0xk/image/upload/v1764290950/instagram-icon_a8uutz.svg');
                  background-repeat:no-repeat;
                  background-position:center;
                  background-size:cover;
                ">
              </a>
            </td>`;
        }

        if (p.link_kwai && p.link_kwai !== "null") {

          html += `
            <td>
              <a href="${p.link_kwai}" target="_blank"
                style="
                  display:inline-block;
                  width:32px;
                  height:32px;
                  border-radius:20%;
                  background-image:url('/static/img/kwai.svg');
                  background-repeat:no-repeat;
                  background-position:center;
                  background-size:cover;
                ">
              </a>
            </td>`;
        }

        html += "</tr>";
      });

      tbody.innerHTML = html;

    })
    .catch(err => console.error("Erro fetch projetos:", err));

});