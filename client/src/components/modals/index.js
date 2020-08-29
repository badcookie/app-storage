import AddAppModal from "./AddAppModal";
import UpdateAppModal from "./UpdateAppModal";

const typeModalMap = {
  add: AddAppModal,
  remove: "",
  update: UpdateAppModal
};

const getModal = actionType => typeModalMap[actionType];

export default getModal;
