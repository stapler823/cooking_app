// websocket
var socket = io.connect('http://' + document.domain + ':' + location.port);
var server_p = null
var client_p = null
var ingredient_div = null
var ingredients_list = []

// サーバからのデータ受信で起動
socket.on('message', function(data) {
  // textの場合
  if (data.type === 'text') {
    // 初期時p要素追加
    if (server_p == null && data.data !== '<END_OF_MESSAGE>') {
      server_p = document.createElement('p');
      document.querySelector('#chat').appendChild(server_p);
    }
    // メッセージ途中は同じp要素に文字追加
    if (data.data !== '<END_OF_MESSAGE>') {
      server_p.innerText += data.data;
    } else {
      // メッセージ終了時初期化
      server_p.innerText += "\n--------------------------------------------------------------------------------------------\n";
      server_p = null
    }
  } else {

    // 材料リストがすでに存在している場合は削除(後続で既存の材料も含めたリストを再作成するため)
    if(document.getElementsByClassName('ingredients-list').length) {
      document.querySelector(".ingredients-list").remove();
    }

    // 材料リストを作る
    ingredient_div = document.createElement('div');
    ingredient_div.classList.add("ingredients-list");
    document.querySelector('#modal-body').appendChild(ingredient_div);
    ingredients_list = ingredients_list.concat(data.data);
    // 重複込みの全ての材料リストを作る
    // ingredients_list.push(data.data)

    // 重複なしの材料リストを作る
    var groupedDictionary = [];

    ingredients_list.forEach(function (item) {
      var ingredient = item.ingredient;
      var amount = item.amount;
      console.log(amount);
      // グループ化された辞書型のエントリが既存のキーを持つ場合
      var existingEntry = groupedDictionary.find(function (entry) {
        return entry.ingredient === ingredient;
      });
    
      if (existingEntry) {
        existingEntry.amount.push(amount);
      } else {
        // 新しいキーの場合、新しいエントリを作成
        groupedDictionary.push({ ingredient: ingredient, amount: [amount] });
      }
    });
    // 結果を表示

    var new_ingredients_list = document.createElement("ul");


    // 上記でまとめた材料、分量リストを出力する
    groupedDictionary.forEach(function (item) {
    //   ingredient_div.innerText += "・ " + item.ingredient + ": |";
    //   item.amount.forEach( (amount, i) => 
    //   ingredient_div.innerText += amount + "| "
    // )

    //   ingredient_div.innerText += " \n";
    
    var list_item = document.createElement("li");
    list_item.innerText += item.ingredient + ": ";
    item.amount.forEach( (amount, i) => 
    list_item.innerText += amount + " | "
    )

    // 分量の最後の「| 」を削除する
    list_item.innerText = list_item.innerText.slice(0, -2);

    // 材料リストに格納する
    new_ingredients_list.appendChild(list_item);

    })
    ingredient_div.appendChild(new_ingredients_list);
  }
});

// 入力フォームで「送信」押下後に起動する
document.querySelector('#form').addEventListener('submit', function(e) {
  e.preventDefault();
  var message = document.querySelector('#user_input').value;
  client_p = document.createElement('p');
  client_p.textContent = "入力ワード: " + message;
  document.querySelector('#chat').appendChild(client_p);
  // サーバと連携する
  socket.emit('message', message);
  document.querySelector('#user_input').value = ''
});