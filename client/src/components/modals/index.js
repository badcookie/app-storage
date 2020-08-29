const typeModalMap = {
  add: "",
  remove: "",
  update: ""
};

const getModal = actionType => typeModalMap[actionType];

export default getModal;
