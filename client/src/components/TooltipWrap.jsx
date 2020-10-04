import React from "react";
import { OverlayTrigger, Tooltip } from "react-bootstrap";

const TooltipWrap = ({ message, base }) => {
  const tooltip = <Tooltip>{message}</Tooltip>;
  return (
    <OverlayTrigger placement="top" overlay={tooltip}>
      {base}
    </OverlayTrigger>
  );
};

export default TooltipWrap;
