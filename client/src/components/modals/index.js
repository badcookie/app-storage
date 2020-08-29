import AddAppModal from "./AddAppModal";
import RemoveAppModal from "./RemoveAppModal";
import UpdateAppModal from "./UpdateAppModal";

const typeModalMap = {
  add: AddAppModal,
  remove: RemoveAppModal,
  update: UpdateAppModal
};

const getModal = actionType => typeModalMap[actionType];

export default getModal;
